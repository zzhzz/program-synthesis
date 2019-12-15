import ply.lex as lex
import ply.yacc as yacc

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


def p_sygus_problem_2(p):
    "sygus_problem : cmd_list_non"


def p_cmd_list_non_1(p):
    "cmd_list_non : cmd"


def p_cmd_list_non_2(p):
    "cmd_list_non : cmd cmd_list_non"


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


def p_symbol(p):
    "symbol : SYMBOL"
    print("p_symbol", p[1])


def p_string(p):
    "string : STRING"


def p_literal_int(p):
    "literal : INT"
    print("p_literal_int", p[1])


def p_literal_true(p):
    "literal : BOOL_TRUE"


def p_literal_false(p):
    "literal : BOOL_FALSE"


def p_sort_expr_1(p):
    "sort_expr : SORT_INT"
    print("p_sort_expr_1", p[1])


def p_sort_expr_2(p):
    "sort_expr : SORT_BOOL"
    print("p_sort_expr_2", p[1])


def p_sort_expr_3(p):
    "sort_expr : symbol"


def p_sort_expr_list_1(p):
    "sort_expr_list : "


def p_sort_expr_list_2(p):
    "sort_expr_list : sort_expr sort_expr_list"


def p_term_1(p):
    "term : LB symbol term_list RB"


def p_term_2(p):
    "term : literal"


def p_term_3(p):
    "term : symbol"


def p_term_4(p):
    "term : let_term"


def p_term_list_1(p):
    "term_list : "


def p_term_list_2(p):
    "term_list : term term_list"


def p_let_clause(p):
    "let_clause : LB symbol sort_expr term RB"


def p_let_clause_list_non_1(p):
    "let_clause_list_non : let_clause"


def p_let_clause_list_non_2(p):
    "let_clause_list_non : let_clause let_clause_list_non"


def p_let_term(p):
    "let_term : LB LET LB let_clause_list_non RB term RB"


def p_gterm_1(p):
    "gterm : LB symbol gterm_list RB"


def p_gterm_2(p):
    "gterm : literal"


def p_gterm_3(p):
    "gterm : symbol"


def p_gterm_4(p):
    "gterm : let_gterm"


def p_gterm_5(p):
    "gterm : LB EXP_CONSTANT sort_expr RB"


def p_gterm_6(p):
    "gterm : LB EXP_VARIABLE sort_expr RB"


def p_gterm_7(p):
    "gterm : LB EXP_INPUT_VARIABLE sort_expr RB"


def p_gterm_8(p):
    "gterm : LB EXP_LOCAL_VARIABLE sort_expr RB"


def p_gterm_list_1(p):
    "gterm_list : "


def p_gterm_list_2(p):
    "gterm_list : gterm gterm_list"


def p_let_gclause(p):
    "let_gclause : LB symbol sort_expr gterm RB"


def p_let_gclause_list_non_1(p):
    "let_gclause_list_non : let_gclause"


def p_let_gclause_list_non_2(p):
    "let_gclause_list_non : let_gclause let_gclause_list_non"


def p_let_gterm(p):
    "let_gterm : LB LET LB let_gclause_list_non RB gterm RB"


def p_param(p):
    "param : LB symbol sort_expr RB"


def p_param_list_1(p):
    "param_list : "


def p_param_list_2(p):
    "param_list : param param_list"


def p_gterm_list_non_1(p):
    "gterm_list_non : gterm"


def p_gterm_list_non_2(p):
    "gterm_list_non : gterm gterm_list_non "


def p_ntdef(p):
    "ntdef : LB symbol sort_expr LB gterm_list_non RB RB"


def p_ntdef_list_non_1(p):
    "ntdef_list_non : ntdef"


def p_ntdef_list_non_2(p):
    "ntdef_list_non : ntdef ntdef_list_non"


def p_cmd_set_logic(p):
    "cmd_set_logic : LB CMD_SET_LOGIC symbol RB"


def p_cmd_define_sort(p):
    "cmd_define_sort : LB CMD_DEFINE_SORT symbol sort_expr RB"


def p_cmd_declare_var(p):
    "cmd_declare_var : LB CMD_DECLARE_VAR symbol sort_expr RB"


def p_cmd_declare_fun(p):
    "cmd_declare_fun : LB CMD_DECLARE_FUN symbol LB sort_expr_list RB sort_expr RB"


def p_cmd_define_fun(p):
    "cmd_define_fun : LB CMD_DEFINE_FUN symbol LB param_list RB sort_expr term RB"


def p_cmd_synth_fun(p):
    "cmd_synth_fun : LB CMD_SYNTH_FUN symbol LB param_list RB sort_expr LB ntdef_list_non RB RB"


def p_cmd_constraint(p):
    "cmd_constraint : LB CMD_CONSTRAINT term RB"


def p_cmd_check_synth(p):
    "cmd_check_synth : LB CMD_CHECK_SYNTH RB"


def p_option(p):
    "option : LB symbol string RB"


def p_option_list_non_1(p):
    "option_list_non : option"


def p_option_list_non_2(p):
    "option_list_non : option option_list_non"


def p_cmd_set_options(p):
    "cmd_set_options : LB CMD_SET_OPTIONS LB option_list_non RB RB"


def p_error(p):
    print("error", p)


parser = yacc.yacc(start="sygus_problem")

