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

from itertools import count
import numpy as np


class SygusGraph:
    NODE_EMBEDDING = {
        "link_func": [16],
        "link_literal_bool": [2],
        "link_literal_int_small": [40],
        "link_literal_int_large": [2],
        "link_local": [20],
        "super_and": [1],
        "nonterminal": [20],
        "synth_rule": [20, 40],
        "ast_global": [20],
        "ast_func": [16],
        "ast_synth" : [1],
        "ast_literal_bool": [2],
        "ast_literal_int_small": [40],
        "ast_literal_int_large": [2],
    }

    NODE_EMBEDDING_NUMS = 0

    INTERNAL_FUNCS = [
        "+",
        "-",
        "*",
        "/",
        "mod",
        ">",
        ">=",
        "<",
        "<=",
        "=",
        "and",
        "or",
        "not",
        "=>",
        "ite",
    ]

    INTERNAL_FUNCS_REVERSE = {}

    NODE_EMBEDDING_ARRAY = {}

    @staticmethod
    def init_array():
        cur_count = 0
        for key, shape in SygusGraph.NODE_EMBEDDING.items():
            m = 1
            for x in shape:
                m *= x
            SygusGraph.NODE_EMBEDDING_ARRAY[key] = np.reshape(
                np.arange(m, dtype=np.int32) + cur_count, shape
            )
            cur_count += m

        SygusGraph.INTERNAL_FUNCS_REVERSE = {
            x: i for i, x in enumerate(SygusGraph.INTERNAL_FUNCS)
        }
        NODE_EMBEDDING_NUMS = cur_count

    EDGE_TYPES = {"AST": 0, "ASTLINK": 1, "GEN": 2, "GENLINK": 3, "GENOUT": 4, "PARAMLINK": 5}

    def __init__(self):
        self.nodes = []
        self.edges = []

        self.non_terminal_count = iter(range(20))
        self.non_terminal_gen_count = [iter(range(40)) for _ in range(20)]
        self.global_counter = iter(range(20))
        self.local_counter = iter(range(20))

        self.add_links()

    def add_links(self):
        assert len(self.nodes) == 0
        links = (
            "link_func",
            "link_literal_bool",
            "link_literal_int_small",
            "link_literal_int_large",
            "link_local",
            "super_and",
        )
        for l in links:
            for i in SygusGraph.NODE_EMBEDDING_ARRAY[l]:
                node, _ = self.add_node(i)
                assert node == i

    def add_edge(self, u, v, t):
        self.edges.append((u, v, SygusGraph.EDGE_TYPES[t]))

    def add_node(self, val=None):
        r = len(self.nodes)
        self.nodes.append(val)
        return r, val

    def set_node(self, node, val):
        self.nodes[node] = val

    def add_non_terminal(self):
        r = next(self.non_terminal_count)
        node, _ = self.add_node(SygusGraph.NODE_EMBEDDING_ARRAY["nonterminal"][r])
        return node, r

    def add_gen_rule(self, non_terminal):
        r = next(self.non_terminal_gen_count[non_terminal])
        node, _ = self.add_node(
            SygusGraph.NODE_EMBEDDING_ARRAY["synth_rule"][non_terminal, r]
        )
        return node, r

    def add_func(self, name):
        funcid = SygusGraph.INTERNAL_FUNCS_REVERSE[name]
        node, _ = self.add_node(SygusGraph.NODE_EMBEDDING_ARRAY["ast_func"][funcid])
        link = SygusGraph.NODE_EMBEDDING_ARRAY["link_func"][funcid]
        self.add_edge(node, link, "ASTLINK")
        return node, funcid

    def add_synth_func(self):
        node, _ = self.add_node(SygusGraph.NODE_EMBEDDING_ARRAY["ast_synth"][0])
        return node, 0

    def link_id_literal(self, val):
        if val is True:
            return SygusGraph.NODE_EMBEDDING_ARRAY["link_literal_bool"][1]
        elif val is False:
            return SygusGraph.NODE_EMBEDDING_ARRAY["link_literal_bool"][0]
        else:
            if val >= -20 and val < 20:
                return SygusGraph.NODE_EMBEDDING_ARRAY["link_literal_int_small"][
                    val + 20
                ]
            else:
                return SygusGraph.NODE_EMBEDDING_ARRAY["link_literal_int_large"][
                    1 if val > 0 else 0
                ]

    def add_ast_literal(self, val):
        if val is True:
            node, _ = self.add_node(SygusGraph.NODE_EMBEDDING_ARRAY["ast_literal_bool"][1])
        elif val is False:
            node, _ = self.add_node(SygusGraph.NODE_EMBEDDING_ARRAY["ast_literal_bool"][0])
        else:
            node, _ = self.add_node()
            if val >= -20 and val < 20:
                self.set_node(
                    node, SygusGraph.NODE_EMBEDDING_ARRAY["ast_literal_int_small"][val + 20]
                )
            else:
                self.set_node(
                    node,
                    SygusGraph.NODE_EMBEDDING_ARRAY["ast_literal_int_large"][
                        1 if val > 0 else 0
                    ],
                )
        link = self.link_id_literal(val)
        self.add_edge(node, link, "ASTLINK")
        return node, val

    def add_ast_global_ex(self, r):
        node, _ = self.add_node()
        self.set_node(node, SygusGraph.NODE_EMBEDDING_ARRAY["ast_global"][r])
        return node, r


SygusGraph.init_array()


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
        self.defines = {}
        self.decls = {}
        self.synths = {}
        self.internals = {}
        self.constraints = []
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
            return self.defines[det].sort
        if det in self.decls:
            return self.decls[det].sort
        if det in self.synths:
            return self.synths[det].sort
        if det in self.internals:
            return self.internals[det].sort
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
            sort = self.lookup_func_sort(det)
            r = Expr.build_func(expr.name, children)
            r.sort = sort
            return r
        elif expr.type == ExprType.Let:
            raise Exception("Let clause is not supported")
            lets = tuple(
                (LetClause(c.name, c.sort, self.lookup_expr(c.expr)) for c in expr.lets)
            )
            for c in lets:
                if c.expr.sort != c.sort:
                    raise Exception(
                        f"Let clause wrong type: {c.expr} {c.expr.sort} {c.sort}"
                    )
            self.push_locals({c.name: c.sort for c in lets})
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
        self.push_locals({r.name: r.sort for r in rules})
        rules = tuple(
            (GenRule(r.name, r.sort, self.lookup_exprs(r.exprs)) for r in rules)
        )
        for r in rules:
            for e in r.exprs:
                if r.sort != e.sort:
                    raise Exception(f"Synth rule wrong type: {e} {e.sort} {r.sort}")
        self.pop_locals()
        return rules

    def lookup_det(self, det):
        return FuncDet(det.name, tuple((self.lookup_sort(x) for x in det.paramsorts)))

    def expr_to_graph(self, expr):
        if expr.type == ExprType.Literal:
            node, _ = self.graph.add_ast_literal(expr.value)
            return node
        elif expr.type == ExprType.Func:
            if expr.name in self.global_mapping:
                assert len(expr.children) == 0
                node, _ = self.graph.add_ast_global_ex(self.global_mapping[expr.name])
                return node
            if expr.name == self.synth_name:
                node, _ = self.graph.add_synth_func()
                for i, child in enumerate(expr.children):
                    child_node = self.expr_to_graph(child)
                    self.graph.add_edge(node, child_node, "AST")
                    link = SygusGraph.NODE_EMBEDDING_ARRAY["link_local"][i]
                    self.graph.add_edge(child_node, link, "PARAMLINK")
                return node
            if expr.name in SygusGraph.INTERNAL_FUNCS_REVERSE:
                node, _ = self.graph.add_func(expr.name)
                for child in expr.children:
                    child_node = self.expr_to_graph(child)
                    self.graph.add_edge(node, child_node, "AST")
                return node
            else:
                print(list(SygusGraph.INTERNAL_FUNCS_REVERSE))
                print(expr.name)
                raise Exception("Unknown Name")
        elif expr.type == ExprType.Let:
            raise Exception("Let clause is not supported")

    def expr_links(self, expr, linkfrom):
        if expr.type == ExprType.Literal:
            link = self.graph.link_id_literal(expr.value)
            self.graph.add_edge(linkfrom, link, "GENLINK")
        elif expr.type == ExprType.Func:
            if expr.name in self.local_mapping:
                link = SygusGraph.NODE_EMBEDDING_ARRAY["link_local"][self.local_mapping[expr.name]]
                self.graph.add_edge(linkfrom, link, "GENLINK")
            elif expr.name in self.rule_mapping:
                node, _ = self.rule_mapping[expr.name]
                self.graph.add_edge(linkfrom, node, "GENOUT")
            elif expr.name in SygusGraph.INTERNAL_FUNCS_REVERSE:
                funcid = SygusGraph.INTERNAL_FUNCS_REVERSE[expr.name]
                link = SygusGraph.NODE_EMBEDDING_ARRAY["link_func"][funcid]
                self.graph.add_edge(linkfrom, link, "GENLINK")
                self.expr_links(expr, linkfrom)
            else:
                raise Exception(f"Unknown expr name: {expr.name}")
        else:
            raise Exception(f"Unknown expr type: {expr.type}")


    def check_synth(self):
        self.graph = graph = SygusGraph()
        self.superand = superand = int(graph.NODE_EMBEDDING_ARRAY["super_and"][0])

        self.global_mapping = {decl.det.name: i for i, decl in enumerate(self.decls.values())}
        self.synth = synth = next(iter(self.synths.values()))
        self.local_mapping = {x: i for i, x in enumerate(synth.params)}
        self.synth_name = synth.det.name
        assert len(self.global_mapping) < 20
        assert len(self.local_mapping) < 20

        for con in self.constraints:
            node_child = self.expr_to_graph(con)
            self.graph.add_edge(superand, node_child, "AST")

        self.rule_mapping = {}
        for rule in synth.rules:
            node_root, id_root = self.graph.add_non_terminal()
            self.rule_mapping[rule.name] = node_root, id_root
        self.graph.rule_mapping = {}
        for rule in synth.rules:
            node_root, id_root = self.rule_mapping[rule.name]
            self.graph.rule_mapping[rule.name] = (node_root, [])
            for expr in rule.exprs:
                node_child, _ = self.graph.add_gen_rule(id_root)
                self.graph.add_edge(node_root, node_child, "GEN")
                self.graph.rule_mapping[rule.name][1].append(node_child)

    def push_locals(self, locals):
        self.local_envs.append(locals)

    def pop_locals(self):
        self.local_envs.pop()

    def solve(self, sygusproblem):
        self.sort_table = {}
        self.defines = {}
        self.decls = {}
        self.synths = {}
        self.constraints = []
        self.local_envs = []

        if sygusproblem.cmd_set_logic is not None:
            if sygusproblem.cmd_set_logic.logic != "LIA":
                raise Exception("'LIA' is the only supported logic.")
        for cmd in sygusproblem.cmd_list:
            if isinstance(cmd, CmdDeclFun):
                det = self.lookup_det(cmd.det)
                self.ensure_none(det)
                sort = self.lookup_sort(cmd.sort)
                self.decls[det.to_tuple()] = CmdDeclFun(det, sort)
            elif isinstance(cmd, CmdDefFun):
                det = self.lookup_det(cmd.det)
                self.ensure_none(det)
                params = cmd.params
                sort = self.lookup_sort(cmd.sort)
                self.push_locals(dict(zip(params, det.paramsorts)))
                expr = self.lookup_expr(cmd.expr)
                self.pop_locals()
                if expr.sort != sort:
                    raise Exception(f"Func wrong type: {expr} {expr.sort} {sort}")
                self.defines[det.to_tuple()] = CmdDefFun(det, params, sort, expr)
                raise Exception("define-fun is currently not supported")
            elif isinstance(cmd, CmdSynthFun):
                det = self.lookup_det(cmd.det)
                self.ensure_none(det)
                params = cmd.params
                self.ensure_distinct(params)
                sort = self.lookup_sort(cmd.sort)
                self.push_locals(dict(zip(params, det.paramsorts)))
                rules = self.lookup_rules(cmd.rules)
                self.pop_locals()
                for r in rules:
                    if r.name == "Start":
                        if sort != r.sort:
                            raise Exception(
                                f"Synth func type mismatch: {det.name} {sort} {r.sort}"
                            )
                self.synths[det.to_tuple()] = CmdSynthFun(det, params, sort, rules)
                if len(self.synths) > 1:
                    raise Exception("Multi synth-fun is currently not supported")
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
                return self.graph
            else:
                raise Exception(f"Unknown cmd type: {cmd}")

