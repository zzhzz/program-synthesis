
%{

%}

%token LB RB
%token BOOL_TRUE BOOL_FALSE
%token INT STRING
%token SORT_INT SORT_BOOL
%token CMD_SET_LOGIC CMD_DEFINE_SORT CMD_DECLARE_VAR CMD_DECLARE_FUN
%token CMD_DEFINE_FUN CMD_SYNTH_FUN CMD_CONSTRAINT
%token CMD_CHECK_SYNTH CMD_SET_OPTIONS
%token LET
%token EXP_CONSTANT EXP_VARIABLE EXP_INPUT_VARIABLE EXP_LOCAL_VARIABLE
%token SYMBOL

%%

sygus_problem
    : cmd_set_logic cmd_list_non {}
    | cmd_list_non {}
    ;

cmd_list_non
    : cmd {}
    | cmd cmd_list_non {}
    ;

cmd
    : cmd_define_sort {}
    | cmd_declare_var {}
    | cmd_declare_fun {}
    | cmd_define_fun {}
    | cmd_synth_fun {}
    | cmd_constraint {}
    | cmd_check_synth {}
    | cmd_set_options {}
    ;

symbol
    : SYMBOL {}
    ;

string
    : STRING {}
    ;

literal
    : INT {}
    | BOOL_TRUE {}
    | BOOL_FALSE {}
    ;

sort_expr
    : SORT_INT {}
    | SORT_BOOL {}
    | symbol {}
    ;

sort_expr_list
    : {}
    | sort_expr sort_expr_list {}
    ;

term
    : LB symbol term_list RB {}
    | literal {}
    | symbol {}
    | let_term {}
    ;

term_list
    : {}
    | term term_list {}
    ;

let_clause
    : LB symbol sort_expr term RB {}
    ;

let_clause_list_non
    : let_clause {}
    | let_clause let_clause_list_non {}
    ;

let_term
    : LB LET LB let_clause_list_non RB term RB {}
    ;

gterm
    : LB symbol gterm_list RB {}
    | literal {}
    | symbol {}
    | let_gterm {}
    | LB EXP_CONSTANT sort_expr RB {}
    | LB EXP_VARIABLE sort_expr RB {}
    | LB EXP_INPUT_VARIABLE sort_expr RB {}
    | LB EXP_LOCAL_VARIABLE sort_expr RB {}
    ;

gterm_list
    : {}
    | gterm gterm_list {}
    ;

let_gclause
    : LB symbol sort_expr gterm RB {}
    ;

let_gclause_list_non
    : let_gclause {}
    | let_gclause let_gclause_list_non {}
    ;

let_gterm
    : LB LET LB let_gclause_list_non RB gterm RB {}
    ;

param
    : LB symbol sort_expr RB {}
    ;

param_list
    : {}
    | param param_list {}
    ;

gterm_list_non
    : gterm {}
    | gterm gterm_list_non {}
    ;

ntdef
    : LB symbol sort_expr LB gterm_list_non RB RB {}
    ;

ntdef_list_non
    : ntdef {}
    | ntdef ntdef_list_non {}
    ;

cmd_set_logic
    : LB CMD_SET_LOGIC symbol RB {}
    ;

cmd_define_sort
    : LB CMD_DEFINE_SORT symbol sort_expr RB {}
    ;

cmd_declare_var
    : LB CMD_DECLARE_VAR symbol sort_expr RB {}
    ;

cmd_declare_fun
    : LB CMD_DECLARE_FUN symbol LB sort_expr_list RB sort_expr RB {}
    ;

cmd_define_fun
    : LB CMD_DEFINE_FUN symbol LB param_list RB sort_expr term RB
    ;

cmd_synth_fun
    : LB CMD_SYNTH_FUN symbol LB param_list RB sort_expr LB ntdef_list_non RB RB
    ;

cmd_constraint
    : LB CMD_CONSTRAINT term RB {}
    ;

cmd_check_synth
    : LB CMD_CHECK_SYNTH RB {}
    ;

option
    : LB symbol string RB {}
    ;

option_list_non
    : option {}
    | option option_list_non {}
    ;

cmd_set_options
    : LB CMD_SET_OPTIONS LB option_list_non RB RB {}
    ;

%%