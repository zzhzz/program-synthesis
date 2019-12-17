from sygusparser import parser
from sygustree import (
    CmdCheckSynth,
    CmdConstraint,
    CmdDeclFun,
    CmdDefFun,
    CmdDefSort,
    CmdSetLogic,
    CmdSetOptions,
    CmdSynthFun,
    Expr,
    ExprType,
    FuncDet,
    GenRule,
    LetClause,
    Option,
    Sort,
    SortValue,
    SygusProblem,
)

import z3
import time

from itertools import count
from collections import deque, defaultdict


class SygusSolver:

    INTERNALS = [
        ("+", (SortValue.Int, SortValue.Int), SortValue.Int),
        ("-", (SortValue.Int, SortValue.Int), SortValue.Int),
        ("*", (SortValue.Int, SortValue.Int), SortValue.Int),
        ("/", (SortValue.Int, SortValue.Int), SortValue.Int),
        ("mod", (SortValue.Int, SortValue.Int), SortValue.Int),
        (">", (SortValue.Int, SortValue.Int), SortValue.Bool),
        (">=", (SortValue.Int, SortValue.Int), SortValue.Bool),
        ("<", (SortValue.Int, SortValue.Int), SortValue.Bool),
        ("<=", (SortValue.Int, SortValue.Int), SortValue.Bool),
        ("=", (SortValue.Int, SortValue.Int), SortValue.Bool),
        ("and", (SortValue.Bool, SortValue.Bool), SortValue.Bool),
        ("or", (SortValue.Bool, SortValue.Bool), SortValue.Bool),
        ("=>", (SortValue.Bool, SortValue.Bool), SortValue.Bool),
        ("not", (SortValue.Bool,), SortValue.Bool),
        ("ite", (SortValue.Bool, SortValue.Int, SortValue.Int), SortValue.Int),
        ("ite", (SortValue.Bool, SortValue.Bool, SortValue.Bool), SortValue.Bool),
    ]

    def __init__(self):
        self.sort_table = {}
        self.internals = {}
        self.local_envs = []
        self.add_internals()

    def add_internals(self):
        for name, params, sort in SygusSolver.INTERNALS:
            det = FuncDet(name, params)
            cmd = CmdDeclFun(det, sort)
            self.internals[det.to_tuple()] = cmd

    def ensure_none(self, det):
        det = det.to_tuple()
        if (
            det in self.defines
            or det in self.decls
            or det in self.synths
            or det in self.internals
        ):
            raise Exception(f"Function '{det}' alerady exists.")

    def ensure_distinct(self, names):
        a = set()
        for n in names:
            if n in a:
                raise Exception(f"names not distinct: {names}")
            a.add(n)

    def lookup_sort(self, sort):
        if sort.value is not None:
            return sort.value
        if sort.name is not None:
            if sort.name in self.sort_table:
                return self.sort_table[sort.name]
            raise Exception(f"Unknown sort name '{sort.name}'.")
        raise Exception(f"Invalid sort.")

    def lookup_func_sort(self, det):
        det = det.to_tuple()
        if len(det) == 1:
            for d in self.local_envs[::-1]:
                if det[0] in d:
                    return d[det[0]]
        if det in self.defines:
            return self.defines_rename[self.defines[det]].sort, self.defines[det]
        if det in self.decls:
            return self.decls_rename[self.decls[det]].sort, self.decls[det]
        if det in self.synths:
            return self.synths_rename[self.synths[det]].sort, self.synths[det]
        if det in self.internals:
            return self.internals[det].sort, det[0]
        raise Exception(f"Failed to find function: {det}")

    def lookup_exprs(self, exprs):
        return tuple((self.lookup_expr(expr) for expr in exprs))

    def lookup_expr(self, expr):
        if expr.type == ExprType.Literal:
            return expr
        elif expr.type == ExprType.Func:
            children = tuple(
                (self.lookup_expr(childexpr) for childexpr in expr.children)
            )
            det = FuncDet(expr.name, tuple((c.sort for c in children)))
            sort, newname = self.lookup_func_sort(det)
            r = Expr.build_func(newname, children)
            r.sort = sort
            return r
        elif expr.type == ExprType.Let:
            newnames = [self.new_local(c.sort, "l") for c in expr.lets]
            lets = tuple(
                (LetClause(c.name, c.sort, self.lookup_expr(c.expr)) for c in expr.lets)
            )
            for c in lets:
                if c.expr.sort != c.sort:
                    raise Exception(
                        f"Let clause wrong type: {c.expr} {c.expr.sort} {c.sort}"
                    )
            self.push_locals(
                {c.name: (c.sort, newname) for c, newname in zip(lets, newnames)}
            )
            lets = tuple(
                (
                    LetClause(newname, c.sort, c.expr)
                    for c, newname in zip(lets, newnames)
                )
            )
            child = self.lookup_expr(self, expr.children[0])
            self.pop_locals()
            r = Expr.build_let(lets, child)
            r.sort = child.sort
            return r
        elif expr.type in (
            ExprType.ExpConstant,
            ExprType.ExpVariable,
            ExprType.ExpInputVariable,
            ExprType.ExpLocalVariable,
        ):
            return expr
        else:
            raise Exception(f"Invalid Expr Type: {expr.type}")

    def lookup_rules(self, rules):
        rules = tuple(
            (GenRule(r.name, self.lookup_sort(r.sort), r.exprs) for r in rules)
        )
        symbols = [r.name for r in rules]
        self.ensure_distinct(symbols)
        if "Start" not in symbols:
            raise Exception("Start not in synth rules")
        newnames = [
            self.new_local(r.sort, "s") if r.name != "Start" else "Start" for r in rules
        ]
        self.push_locals(
            {r.name: (r.sort, newname) for r, newname in zip(rules, newnames)}
        )
        rules = tuple(
            [
                GenRule(newname, r.sort, self.lookup_exprs(r.exprs))
                for r, newname in zip(rules, newnames)
            ]
        )
        for r in rules:
            for e in r.exprs:
                if r.sort != e.sort:
                    raise Exception(f"Synth rule wrong type: {e} {e.sort} {r.sort}")
        self.pop_locals()
        return rules

    def lookup_det(self, det):
        return FuncDet(det.name, tuple((self.lookup_sort(x) for x in det.paramsorts)))

    def expand_left(self, expr):
        for i, child in enumerate(expr):
            if child in self.synth_rules:
                results = self.synth_rules[child]
                newresults = [expr[:i] + result + expr[i + 1 :] for result in results]
                return newresults
        return None

    def list_expr_to_string(self, expr):
        # if isinstance(expr, list):
        #     return f"({' '.join(self.list_expr_to_string(e) for e in expr)})"
        # return str(expr)
        return ' '.join(expr)

    def expr_to_define_cmd(self, expr):
        # return ' '.join(expr)
        name = self.synthcmd.det.name
        params_sort = self.synthcmd.det.paramsorts
        params_name = self.synthcmd.params
        params_str = " ".join(
            [f"({n} {str(s)})" for s, n in zip(params_sort, params_name)]
        )
        return f"(define-fun {name} ({params_str}) {self.synthcmd.sort} {self.list_expr_to_string(expr)})"

    def check_valid(self, expr):
        cmd_define_func = self.expr_to_define_cmd(expr)
        cmd_check = "(check-sat)"
        all_cmds = (
            self.cmd_declears_str
            + [cmd_define_func]
            + [self.constraint_combine_str]
            + [cmd_check]
        )
        all_cmds = "\n".join(all_cmds)
        # print(all_cmds)
        # print()
        all_cmds = z3.parse_smt2_string(all_cmds)
        solver = z3.Solver()
        if solver.check(all_cmds) == z3.unsat:
            print(cmd_define_func)
            return True
        return False

    def check_synth(self):
        # TODO remove these limitation
        assert len(self.defines) == 0
        assert len(self.synths_rename) == 1
        for decl in self.decls_rename.values():
            assert len(decl.det.paramsorts) == 0

        self.synthcmd = synthcmd = next(iter(self.synths_rename.values()))
        self.synth_rules = {
            rule.name: [expr.to_list() for expr in rule.exprs]
            for rule in synthcmd.rules
        }

        constraint_combine = None
        for constraint in self.constraints:
            if constraint_combine is None:
                constraint_combine = constraint
            else:
                constraint_combine = Expr.build_func(
                    "and", (constraint_combine, constraint)
                )
        constraint_combine = Expr.build_func("not", (constraint_combine,))
        self.constraint_combine = CmdConstraint(constraint_combine)
        self.constraint_combine_str = self.constraint_combine.to_assert_str()
        self.cmd_declears_str = [str(f) for f in self.decls_rename.values()]

        expand_queue = deque()
        expand_queue.append(["Start"])

        while len(expand_queue) > 0:
            cur_expr = expand_queue.popleft()
            cur_exprs = self.expand_left(cur_expr)
            if cur_exprs is None:
                if self.check_valid(cur_expr):
                    return True
            else:
                expand_queue.extend(cur_exprs)

    def push_locals(self, locals):
        self.local_envs.append(locals)

    def pop_locals(self):
        self.local_envs.pop()

    def get_new_name(self, funtypeidx):
        counter = self.rename_counter[funtypeidx]
        count = next(counter)
        return funtypeidx + str(count)

    def rename_decl(self, decl):
        if len(decl.det.paramsorts) != 0:
            funtypeidx = "declf"
        else:
            if decl.sort == SortValue.Bool:
                funtypeidx = "declb"
            elif decl.sort == SortValue.Int:
                funtypeidx = "decli"
        return self.get_new_name(funtypeidx)

    def rename_def(self, decl):
        if len(decl.det.paramsorts) != 0:
            funtypeidx = "deff"
        else:
            if decl.sort == SortValue.Bool:
                funtypeidx = "defb"
            elif decl.sort == SortValue.Int:
                funtypeidx = "defi"
        return self.get_new_name(funtypeidx)

    def rename_synth(self, decl):
        funtypeidx = "synth"
        return self.get_new_name(funtypeidx)

    VARIABLE_TABLE = {
        (SortValue.Bool, "pd"): "pdb",
        (SortValue.Int, "pd"): "pdi",
        (SortValue.Bool, "ps"): "psb",
        (SortValue.Int, "ps"): "psi",
        (SortValue.Bool, "l"): "lb",
        (SortValue.Int, "l"): "li",
        (SortValue.Bool, "s"): "sb",
        (SortValue.Int, "s"): "si",
    }

    def new_local(self, sort, t):
        return self.get_new_name(SygusSolver.VARIABLE_TABLE[(sort, t)])

    def solve(self, sygusproblem):
        self.sort_table = {}
        self.constraints = []
        self.local_envs = []
        self.defines = {}
        self.defines_rename = {}
        self.decls = {}
        self.decls_rename = {}
        self.synths = {}
        self.synths_rename = {}

        self.rename_counter = defaultdict(lambda: iter(count()))
        self.rename_back = {}

        if sygusproblem.cmd_set_logic is not None:
            if sygusproblem.cmd_set_logic.logic != "LIA":
                raise Exception("'LIA' is the only supported logic.")
        for cmd in sygusproblem.cmd_list:
            if isinstance(cmd, CmdDeclFun):
                det = self.lookup_det(cmd.det)
                self.ensure_none(det)
                sort = self.lookup_sort(cmd.sort)
                newname = self.rename_decl(CmdDeclFun(det, sort))
                self.decls[det.to_tuple()] = newname
                self.decls_rename[newname] = CmdDeclFun(
                    FuncDet(newname, det.paramsorts), sort
                )
            elif isinstance(cmd, CmdDefFun):
                det = self.lookup_det(cmd.det)
                self.ensure_none(det)
                params = cmd.params
                sort = self.lookup_sort(cmd.sort)
                newnames = [self.new_local(s, "pd") for s in det.paramsorts]
                self.push_locals(dict(zip(params, zip(det.paramsorts, newnames))))
                expr = self.lookup_expr(cmd.expr)
                self.pop_locals()
                if expr.sort != sort:
                    raise Exception(f"Func wrong type: {expr} {expr.sort} {sort}")
                newname = self.rename_def(CmdDefFun(det, params, sort, expr))
                self.defines[det.to_tuple()] = newname
                self.defines_rename[newname] = CmdDefFun(
                    FuncDet(newname, det.paramsorts), newnames, sort, expr
                )
            elif isinstance(cmd, CmdSynthFun):
                det = self.lookup_det(cmd.det)
                self.ensure_none(det)
                params = cmd.params
                self.ensure_distinct(params)
                sort = self.lookup_sort(cmd.sort)
                newnames = [self.new_local(s, "ps") for s in det.paramsorts]
                self.push_locals(dict(zip(params, zip(det.paramsorts, newnames))))
                rules = self.lookup_rules(cmd.rules)
                self.pop_locals()
                for r in rules:
                    if r.name == "Start":
                        if sort != r.sort:
                            raise Exception(
                                f"Synth func type mismatch: {det.name} {sort} {r.sort}"
                            )
                newname = self.rename_synth(CmdSynthFun(det, params, sort, rules))
                self.synths[det.to_tuple()] = newname
                self.synths_rename[newname] = CmdSynthFun(
                    FuncDet(newname, det.paramsorts), newnames, sort, rules
                )
            elif isinstance(cmd, CmdSetOptions):
                pass
            elif isinstance(cmd, CmdDefSort):
                if cmd.name in self.sort_table:
                    raise Exception(f"Sort '{cmd.name}' already exists.")
                cmd.sort_table[cmd.name] = self.lookup_sort(cmd.sort)
            elif isinstance(cmd, CmdConstraint):
                expr = self.lookup_expr(cmd.constraint)
                if expr.sort != SortValue.Bool:
                    raise Exception(f"Expr '{expr}' is not boolean.")
                self.constraints.append(expr)
            elif isinstance(cmd, CmdCheckSynth):
                self.check_synth()
            else:
                raise Exception(f"Unknown cmd type: {cmd}")
