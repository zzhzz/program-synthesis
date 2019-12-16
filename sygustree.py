from enum import Enum
from collections import namedtuple


class SygusProblem:
    def __init__(self, cmd_set_logic, cmd_list):
        self.cmd_set_logic = cmd_set_logic
        self.cmd_list = cmd_list

    def __str__(self):
        return "\n".join(
            ([str(self.cmd_set_logic)] if self.cmd_set_logic else [])
            + list(map(str, self.cmd_list))
        )


class SortValue(Enum):
    Int = 0
    Bool = 1

    def __str__(self):
        if self == SortValue.Int:
            return "Int"
        if self == SortValue.Bool:
            return "Bool"


class LetClause:
    def __init__(self, name, sort, expr):
        self.name = name
        self.sort = sort
        self.expr = expr

    def __str__(self):
        return "(" + self.name + " " + self.sort + " " + self.expr + ")"


class Sort:
    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value
    def __str__(self):
        return self.name or str(self.value)


class ExprType(Enum):
    Literal = 0
    Func = 1
    Let = 2
    ExpConstant = 3
    ExpVariable = 4
    ExpInputVariable = 5
    ExpLocalVariable = 6


class Expr:
    def __init__(self):
        self.sort = None
        self.name = None
        self.value = None
        self.type = None
        self.lets = None
        self.children = None

    @staticmethod
    def build_literal(sort, value):
        r = Expr()
        r.type = ExprType.Literal
        r.sort = sort
        r.value = value
        return r

    @staticmethod
    def build_func(name, children):
        r = Expr()
        r.type = ExprType.Func
        r.name = name
        r.children = children
        return r

    @staticmethod
    def build_let(lets, child):
        r = Expr()
        r.type = ExprType.Let
        r.lets = lets
        r.children = (children,)
        return r

    @staticmethod
    def build_gen(gentype, sort):
        r = Expr()
        r.type = gentype
        r.sort = sort
        return r

    def __str__(self):
        if self.type == ExprType.Literal:
            return str(self.value)
        if self.type == ExprType.Func:
            if len(self.children) == 0:
                return self.name
            return f"({self.name} {' '.join(map(str, self.children))})"
        if self.type == ExprType.Let:
            return f"(let ({' '.join(map(str, self.lets))}) {self.children[0]})"
        else:
            return f"({self.type} {self.sort})"

class GenRule:
    def __init__(self, name, sort, exprs):
        self.name = name
        self.sort = sort
        self.exprs = exprs

    def __str__(self):
        return f"({self.name} {self.sort} ({' '.join(map(str, self.exprs))}))"


class CmdSetLogic:
    def __init__(self, logic):
        self.logic = logic
    def __str__(self):
        return f"(set-logic {self.logic})"


class FuncDet:
    def __init__(self, name, paramsorts):
        self.name = name
        self.paramsorts = paramsorts

    def to_tuple(self):
        return (self.name,) + tuple(self.paramsorts)

    def __str__(self):
        return f"{self.name} ({' '.join(map(str, self.paramsorts))})"


class CmdDeclFun:
    def __init__(self, det, sort):
        self.det = det
        self.sort = sort

    def __str__(self):
        return f"(declare-fun {self.det} {self.sort})"


class CmdDefFun:
    def __init__(self, det, params, sort, expr):
        self.det = det
        self.params = params
        self.sort = sort
        self.expr = expr

    def __str__(self):
        name = self.det.name
        params_sort = self.det.paramsorts
        params_name = self.params
        params_str = ' '.join([f"({n} {str(s)})" for s, n in zip(params_sort, params_name)])
        return f"(define-fun {name} ({params_str}) {self.sort} {self.expr})"

class CmdSynthFun:
    def __init__(self, det, params, sort, rules):
        self.det = det
        self.params = params
        self.sort = sort
        self.rules = rules

    def __str__(self):
        name = self.det.name
        params_sort = self.det.paramsorts
        params_name = self.params
        params_str = ' '.join([f"({n} {str(s)})" for s, n in zip(params_sort, params_name)])
        return f"(synth-fun {name} ({params_str}) {self.sort} ({' '.join(map(str, self.rules))}))"

class CmdSetOptions:
    def __init__(self, options):
        self.options = options

    def __str__(self):
        return f"(set-options ({' '.join(map(str, self.options))}))"


class CmdDefSort:
    def __init__(self, name, sort):
        self.name = name
        self.sort = sort

    def __str__(self):
        return f"(define-sort {self.name} {self.sort})"


class CmdConstraint:
    def __init__(self, constraint):
        self.constraint = constraint

    def to_assert_str(self):
        return f"(assert {self.constraint})"

    def __str__(self):
        return f"(constraint {self.constraint})"


class CmdCheckSynth:
    def __init__(self):
        pass

    def __str__(self):
        return "(check-synth)"


class Option:
    def __init__(self, symbol, string):
        self.symbol = symbol
        self.string = string

    def __str__(self):
        return f"({self.symbol} {self.string})"

