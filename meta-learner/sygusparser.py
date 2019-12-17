import ply.lex as lex
import ply.yacc as yacc

from sygustree import (CmdCheckSynth, CmdConstraint, CmdDeclFun, CmdDefFun,
                       CmdDefSort, CmdSetLogic, CmdSetOptions, CmdSynthFun,
                       Expr, ExprType, FuncDet, GenRule, LetClause, Option,
                       Sort, SortValue, SygusProblem)

__all__ = ("lexer", "parser")


tokens = (
    "LB",
    "RB",
    "BOOL_TRUE",
    "BOOL_FALSE",
    "INT",
    "STRING",
    "SORT_INT",
    "SORT_BOOL",
    "CMD_SET_LOGIC",
    "CMD_DEFINE_SORT",
    "CMD_DECLARE_VAR",
    "CMD_DECLARE_FUN",
    "CMD_DEFINE_FUN",
    "CMD_SYNTH_FUN",
    "CMD_CONSTRAINT",
    "CMD_CHECK_SYNTH",
    "CMD_SET_OPTIONS",
    "LET",
    "EXP_CONSTANT",
    "EXP_VARIABLE",
    "EXP_INPUT_VARIABLE",
    "EXP_LOCAL_VARIABLE",
    "SYMBOL",
)

reserved = {
    "(": "LB",
    ")": "RB",
    "true": "BOOL_TRUE",
    "false": "BOOL_FALSE",
    "Int": "SORT_INT",
    "Bool": "SORT_BOOL",
    "let": "LET",
    "set-logic": "CMD_SET_LOGIC",
    "define-sort": "CMD_DEFINE_SORT",
    "declare-var": "CMD_DECLARE_VAR",
    "declare-fun": "CMD_DECLARE_FUN",
    "define-fun": "CMD_DEFINE_FUN",
    "synth-fun": "CMD_SYNTH_FUN",
    "constraint": "CMD_CONSTRAINT",
    "check-synth": "CMD_CHECK_SYNTH",
    "set-options": "CMD_SET_OPTIONS",
    "Constant": "EXP_CONSTANT",
    "Variable": "EXP_VARIABLE",
    "InputVariable": "EXP_INPUT_VARIABLE",
    "LocalVariable": "EXP_LOCAL_VARIABLE",
}


def t_WHITESPACE(t):
    r"[ \r\n\t]+"
    pass


def t_COMMENT(t):
    r";.*"
    pass


def t_LB(t):
    r"\("
    return t


def t_RB(t):
    r"\)"
    return t


def t_STRING(t):
    r'"[^"]*"'
    return t


def t_SYMBOL(t):
    r"[_\+\-\*&\|!~<>=/%\?\.\$\^a-zA-Z][_\+\-\*&\|!~<>=/%\?\.\$\^a-zA-Z0-9]*"
    t.type = reserved.get(t.value, "SYMBOL")
    return t


def t_INT(t):
    r"-?[0-9]+"
    t.value = int(t.value)
    return t


def t_error(t):
    raise Exception("Illegal character %s" % repr(t.value[0]))


lexer = lex.lex()


def p_sygus_problem_1(p):
    "sygus_problem : cmd_set_logic cmd_list_non"
    p[0] = SygusProblem(p[1], p[2])


def p_sygus_problem_2(p):
    "sygus_problem : cmd_list_non"
    p[0] = SygusProblem(None, p[1])


def p_cmd_list_non_1(p):
    "cmd_list_non : cmd"
    p[0] = (p[1],)


def p_cmd_list_non_2(p):
    "cmd_list_non : cmd cmd_list_non"
    p[0] = (p[1],) + p[2]


def p_cmds(p):
    """
    cmd : cmd_define_sort
        | cmd_declare_var
        | cmd_declare_fun
        | cmd_define_fun
        | cmd_synth_fun
        | cmd_constraint
        | cmd_check_synth
        | cmd_set_options
    """
    p[0] = p[1]


def p_symbol(p):
    "symbol : SYMBOL"
    p[0] = p[1]


def p_string(p):
    "string : STRING"
    p[0] = p[1]


def p_literal_int(p):
    "literal : INT"
    p[0] = Expr.build_literal(SortValue.Int, p[1])


def p_literal_true(p):
    "literal : BOOL_TRUE"
    p[0] = Expr.build_literal(SortValue.Bool, True)


def p_literal_false(p):
    "literal : BOOL_FALSE"
    p[0] = Expr.build_literal(SortValue.Bool, False)


def p_sort_expr_1(p):
    "sort_expr : SORT_INT"
    p[0] = Sort(value=SortValue.Int)


def p_sort_expr_2(p):
    "sort_expr : SORT_BOOL"
    p[0] = Sort(value=SortValue.Bool)


def p_sort_expr_3(p):
    "sort_expr : symbol"
    p[0] = Sort(name=p[1])


def p_sort_expr_list_1(p):
    "sort_expr_list : "
    p[0] = ()


def p_sort_expr_list_2(p):
    "sort_expr_list : sort_expr sort_expr_list"
    p[0] = (p[1],) + p[2]


def p_term_1(p):
    "term : LB symbol term_list RB"
    p[0] = Expr.build_func(p[2], p[3])


def p_term_2(p):
    "term : literal"
    p[0] = p[1]


def p_term_3(p):
    "term : symbol"
    p[0] = Expr.build_func(p[1], ())


def p_term_4(p):
    "term : let_term"
    p[0] = p[1]


def p_term_list_1(p):
    "term_list : "
    p[0] = ()


def p_term_list_2(p):
    "term_list : term term_list"
    p[0] = (p[1],) + p[2]


def p_let_clause(p):
    "let_clause : LB symbol sort_expr term RB"
    p[0] = LetClause(p[0], p[1], p[2])


def p_let_clause_list_non_1(p):
    "let_clause_list_non : let_clause"
    p[0] = (p[1],)


def p_let_clause_list_non_2(p):
    "let_clause_list_non : let_clause let_clause_list_non"
    p[0] = (p[1],) + p[2]


def p_let_term(p):
    "let_term : LB LET LB let_clause_list_non RB term RB"
    p[0] = Expr.build_let(p[4], p[6])


def p_gterm_1(p):
    "gterm : LB symbol gterm_list RB"
    p[0] = Expr.build_func(p[2], p[3])


def p_gterm_2(p):
    "gterm : literal"
    p[0] = p[1]


def p_gterm_3(p):
    "gterm : symbol"
    p[0] = Expr.build_func(p[1], ())


def p_gterm_4(p):
    "gterm : let_gterm"
    p[0] = p[1]


def p_gterm_5(p):
    "gterm : LB EXP_CONSTANT sort_expr RB"
    p[0] = Expr.build_gen(ExprType.ExpConstant, p[3])


def p_gterm_6(p):
    "gterm : LB EXP_VARIABLE sort_expr RB"
    p[0] = Expr.build_gen(ExprType.ExpVariable, p[3])


def p_gterm_7(p):
    "gterm : LB EXP_INPUT_VARIABLE sort_expr RB"
    p[0] = Expr.build_gen(ExprType.ExpInputVariable, p[3])


def p_gterm_8(p):
    "gterm : LB EXP_LOCAL_VARIABLE sort_expr RB"
    p[0] = Expr.build_gen(ExprType.ExpLocalVariable, p[3])


def p_gterm_list_1(p):
    "gterm_list : "
    p[0] = ()


def p_gterm_list_2(p):
    "gterm_list : gterm gterm_list"
    p[0] = (p[1],) + p[2]


def p_let_gclause(p):
    "let_gclause : LB symbol sort_expr gterm RB"
    p[0] = LetClause(p[0], p[1], p[2])


def p_let_gclause_list_non_1(p):
    "let_gclause_list_non : let_gclause"
    p[0] = (p[1],)


def p_let_gclause_list_non_2(p):
    "let_gclause_list_non : let_gclause let_gclause_list_non"
    p[0] = (p[1],) + p[2]


def p_let_gterm(p):
    "let_gterm : LB LET LB let_gclause_list_non RB gterm RB"
    p[0] = Expr.build_let(p[4], p[6])


def p_param(p):
    "param : LB symbol sort_expr RB"
    p[0] = (p[2], p[3])


def p_param_list_1(p):
    "param_list : "
    p[0] = ()


def p_param_list_2(p):
    "param_list : param param_list"
    p[0] = (p[1],) + p[2]


def p_gterm_list_non_1(p):
    "gterm_list_non : gterm"
    p[0] = (p[1],)


def p_gterm_list_non_2(p):
    "gterm_list_non : gterm gterm_list_non "
    p[0] = (p[1],) + p[2]


def p_ntdef(p):
    "ntdef : LB symbol sort_expr LB gterm_list_non RB RB"
    p[0] = GenRule(p[2], p[3], p[5])


def p_ntdef_list_non_1(p):
    "ntdef_list_non : ntdef"
    p[0] = (p[1],)


def p_ntdef_list_non_2(p):
    "ntdef_list_non : ntdef ntdef_list_non"
    p[0] = (p[1],) + p[2]


def p_cmd_set_logic(p):
    "cmd_set_logic : LB CMD_SET_LOGIC symbol RB"
    p[0] = CmdSetLogic(p[3])


def p_cmd_define_sort(p):
    "cmd_define_sort : LB CMD_DEFINE_SORT symbol sort_expr RB"
    p[0] = CmdDefSort(p[3], p[4])


def p_cmd_declare_var(p):
    "cmd_declare_var : LB CMD_DECLARE_VAR symbol sort_expr RB"
    det = FuncDet(p[3], ())
    p[0] = CmdDeclFun(det, p[4])


def p_cmd_declare_fun(p):
    "cmd_declare_fun : LB CMD_DECLARE_FUN symbol LB sort_expr_list RB sort_expr RB"
    det = FuncDet(p[3], p[5])
    p[0] = CmdDeclFun(det, p[7])


def p_cmd_define_fun(p):
    "cmd_define_fun : LB CMD_DEFINE_FUN symbol LB param_list RB sort_expr term RB"
    pname, psort = zip(*p[5])
    det = FuncDet(p[3], psort)
    p[0] = CmdDefFun(det, pname, p[7], p[8])


def p_cmd_synth_fun(p):
    "cmd_synth_fun : LB CMD_SYNTH_FUN symbol LB param_list RB sort_expr LB ntdef_list_non RB RB"
    pname, psort = zip(*p[5])
    det = FuncDet(p[3], psort)
    p[0] = CmdSynthFun(det, pname, p[7], p[9])


def p_cmd_constraint(p):
    "cmd_constraint : LB CMD_CONSTRAINT term RB"
    p[0] = CmdConstraint(p[3])


def p_cmd_check_synth(p):
    "cmd_check_synth : LB CMD_CHECK_SYNTH RB"
    p[0] = CmdCheckSynth()


def p_option(p):
    "option : LB symbol string RB"
    p[0] = Option(p[1], p[2])


def p_option_list_non_1(p):
    "option_list_non : option"
    p[0] = (p[1],)


def p_option_list_non_2(p):
    "option_list_non : option option_list_non"
    p[0] = (p[1],) + p[2]


def p_cmd_set_options(p):
    "cmd_set_options : LB CMD_SET_OPTIONS LB option_list_non RB RB"
    p[0] = CmdSetOptions(p[4])


def p_error(p):
    print("error", p)
    raise Exception(f"error {str(p)}")


parser = yacc.yacc(start="sygus_problem")
