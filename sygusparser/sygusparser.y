%skeleton "lalr1.cc" /* -*- C++ -*- */
%require "3.0"
%language "c++"

%code requires
{
#include <stdio.h>
#include "sygusparser_lexer.hh"

#include <z3++.h>

namespace sygusparser{
    inline int yylex(object**x, sygusparser::sygusparser_lexer &lexer) {
        *x = nullptr;
        return lexer.get_next_token();
    }
}
}

%define api.namespace { sygusparser }
%lex-param { sygusparser::sygusparser_lexer &lexer }
%parse-param { sygusparser::sygusparser_lexer &lexer }
%parse-param { sygus_command_list &cmds }


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

%union{
    void *type_none;
    z3::sort *type_sort;
    z3::sort_vector *type_sort_vector;
    z3::expr *type_expr;
    z3::expr_vector *type_expr_vector;
    string_wrap *type_str;
}

%type <type_none> sygus_problem cmd_list_non cmd cmd_define_sort cmd_declare_var cmd_declare_fun
%type <type_none> cmd_define_fun cmd_synth_fun cmd_constraint cmd_check_synth cmd_set_options
%type <type_str> symbol string
%type <type_expr> literal term
%type <type_expr_vector> term_list
%type <type_sort> sort_expr
%type <type_sort_vector> sort_expr_list


let_clause
let_clause_list_non
let_term
gterm
gterm_list
let_gclause
let_gclause_list_non
let_gterm
param
param_list
gterm_list_non
ntdef
ntdef_list_non


%%
sygus_problem
    : cmd_set_logic cmd_list_non { cmds.add_set_logic(to_shared(dynamic_cast<cmd_set_logic*>($1))); }
    | cmd_list_non {}
    ;

cmd_list_non
    : cmd { cmds.add_cmd(to_shared(dynamic_cast<cmd*>($1))); }
    | cmd cmd_list_non { cmds.add_cmd(to_shared(dynamic_cast<cmd*>($1))); }
    ;

cmd
    : cmd_define_sort { $$ = $1; }
    | cmd_declare_var { $$ = $1; }
    | cmd_declare_fun { $$ = $1; }
    | cmd_define_fun { $$ = $1; }
    | cmd_synth_fun { $$ = $1; }
    | cmd_constraint { $$ = $1; }
    | cmd_check_synth { $$ = $1; }
    | cmd_set_options { $$ = $1; }
    ;

symbol
    : SYMBOL { $$ = new string_wrap(std::string(lexer.YYText())); }
    ;

string
    : STRING { $$ = new string_wrap(std::string(lexer.YYText())); }
    ;

literal
    : INT { $$ = new term_literal(sort_element::sort_elements::Int, atol(lexer.YYText())); }
    | BOOL_TRUE { $$ = new term_literal(sort_element::sort_elements::Bool, 1); }
    | BOOL_FALSE { $$ = new term_literal(sort_element::sort_elements::Bool, 0); }
    ;

sort_expr
    : SORT_INT { $$ = new sort_element(sort_element::sort_elements::Int); }
    | SORT_BOOL { $$ = new sort_element(sort_element::sort_elements::Bool); }
    | symbol { string_wrap* sw = &dynamic_cast<string_wrap&>(*$1); $$ = new sort_symbol(sw->get()); delete sw; }
    ;

sort_expr_list
    : { $$ = new list_wrap<sort>(); }
    | sort_expr sort_expr_list {
        auto lw = &dynamic_cast<list_wrap<sort>&>(*$2);
        lw->add(to_shared_cast<sort>($1));
        $$ = lw;
    }
    ;

term
    : LB symbol term_list RB {
        string_wrap* sw = &dynamic_cast<string_wrap&>(*$1);
        list_wrap<term>* lw = &dynamic_cast<list_wrap<term>&>(*$2);
        $$ = new term_func(sw->get(), lw->get());
        delete sw;
        delete lw;
    }
    | literal { $$ = $1; }
    | symbol { $$ = $1; }
    | let_term { $$ = $1; }
    ;

term_list
    : { $$ = new list_wrap<term>(); }
    | term term_list {
        auto lw = &dynamic_cast<list_wrap<term>&>(*$2);
        lw->add(to_shared_cast<term>($1));
        $$ = lw;
    }
    ;

let_clause
    : LB symbol sort_expr term RB {
        string_wrap* sw = &dynamic_cast<string_wrap&>(*$1);
        $$ = new let_term_item(sw->get(), to_shared_cast<sort>($2), to_shared_cast<term>($3));
        delete sw;
    }
    ;

let_clause_list_non
    : let_clause { $$ = new list_wrap<let_term_item>(); }
    | let_clause let_clause_list_non {
        auto lw = &dynamic_cast<list_wrap<let_term_item>&>(*$2);
        lw->add(to_shared_cast<let_term_item>($1));
        $$ = lw;
    }
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
    : LB CMD_DEFINE_FUN symbol LB param_list RB sort_expr term RB {}
    ;

cmd_synth_fun
    : LB CMD_SYNTH_FUN symbol LB param_list RB sort_expr LB ntdef_list_non RB RB {}
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
inline void sygusparser::parser::error (const std::string& msg)
{
    throw std::runtime_error(msg);
}
