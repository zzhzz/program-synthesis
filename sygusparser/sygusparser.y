%skeleton "lalr1.cc" /* -*- C++ -*- */
%require "3.0"
%language "c++"

%code requires
{
#include <stdio.h>
#include "tree.h"
#include "sygusparser_lexer.hh"

namespace sygusparser{
    template<typename T>
    inline int yylex(T*x, sygusparser::sygusparser_lexer &lexer) {
        // *x = nullptr;
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

// %define api.value.type {object*}

%union
{
    void *type_void;

    sort *type_sort;
    sort_symbol *type_sort_symbol;
    sort_element *type_sort_element;
    term *type_term;
    term_func *type_term_func;
    term_literal *type_term_literal;
    term_symbol *type_term_symbol;
    let_term_item *type_let_term_item;
    term_let *type_term_let;
    term_exp *type_term_exp;
    cmd *type_cmd;
    cmd_set_logic *type_cmd_set_logic;
    cmd_define_sort *type_cmd_define_sort;
    cmd_declare_var *type_cmd_declare_var;
    cmd_declare_fun *type_cmd_declare_fun;
    param *type_param;
    cmd_define_fun *type_cmd_define_fun;
    synth_rule *type_synth_rule;
    cmd_synth_fun *type_cmd_synth_fun;
    cmd_constraint *type_cmd_constraint;
    cmd_check_synth *type_cmd_check_synth;
    option *type_option;
    cmd_set_options *type_cmd_set_options;
    string_wrap *type_string_wrap;

    list_wrap<sort> * type_sort_list;
    list_wrap<sort_symbol> * type_sort_symbol_list;
    list_wrap<sort_element> * type_sort_element_list;
    list_wrap<term> * type_term_list;
    list_wrap<term_func> * type_term_func_list;
    list_wrap<term_literal> * type_term_literal_list;
    list_wrap<term_symbol> * type_term_symbol_list;
    list_wrap<let_term_item> * type_let_term_item_list;
    list_wrap<term_let> * type_term_let_list;
    list_wrap<term_exp> * type_term_exp_list;
    list_wrap<cmd> * type_cmd_list;
    list_wrap<cmd_set_logic> * type_cmd_set_logic_list;
    list_wrap<cmd_define_sort> * type_cmd_define_sort_list;
    list_wrap<cmd_declare_var> * type_cmd_declare_var_list;
    list_wrap<cmd_declare_fun> * type_cmd_declare_fun_list;
    list_wrap<param> * type_param_list;
    list_wrap<cmd_define_fun> * type_cmd_define_fun_list;
    list_wrap<synth_rule> * type_synth_rule_list;
    list_wrap<cmd_synth_fun> * type_cmd_synth_fun_list;
    list_wrap<cmd_constraint> * type_cmd_constraint_list;
    list_wrap<cmd_check_synth> * type_cmd_check_synth_list;
    list_wrap<option> * type_option_list;
    list_wrap<cmd_set_options> * type_cmd_set_options_list;
    list_wrap<string_wrap> * type_string_wrap_list;
}

%type <type_void> sygus_problem
%type <type_cmd_list> cmd_list_non
%type <type_cmd> cmd
%type <type_string_wrap> symbol
%type <type_string_wrap> string
%type <type_term_literal> literal
%type <type_sort> sort_expr
%type <type_sort_list> sort_expr_list
%type <type_term> term
%type <type_term_list> term_list
%type <type_let_term_item> let_clause
%type <type_let_term_item_list> let_clause_list_non
%type <type_term_let> let_term
%type <type_term> gterm
%type <type_term_list> gterm_list
%type <type_let_term_item> let_gclause
%type <type_let_term_item_list> let_gclause_list_non
%type <type_term_let> let_gterm
%type <type_param> param
%type <type_param_list> param_list
%type <type_term_list> gterm_list_non
%type <type_synth_rule> ntdef
%type <type_synth_rule_list> ntdef_list_non
%type <type_cmd_set_logic> cmd_set_logic
%type <type_cmd_define_sort> cmd_define_sort
%type <type_cmd_declare_var> cmd_declare_var
%type <type_cmd_declare_fun> cmd_declare_fun
%type <type_cmd_define_fun> cmd_define_fun
%type <type_cmd_synth_fun> cmd_synth_fun
%type <type_cmd_constraint> cmd_constraint
%type <type_cmd_check_synth> cmd_check_synth
%type <type_option> option
%type <type_option_list> option_list_non
%type <type_cmd_set_options> cmd_set_options

%%
sygus_problem
    : cmd_set_logic cmd_list_non { cmds.add_set_logic(to_shared($1)); }
    | cmd_list_non {}
    ;

cmd_list_non
    : cmd { cmds.add_cmd(to_shared($1)); }
    | cmd cmd_list_non { cmds.add_cmd(to_shared($1)); }
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
    | symbol { string_wrap* sw = $1; $$ = new sort_symbol(sw->get()); delete sw; }
    ;

sort_expr_list
    : { $$ = new list_wrap<sort>(); }
    | sort_expr sort_expr_list {
        $2->add(to_shared<sort>($1));
        $$ = $2;
    }
    ;

term
    : LB symbol term_list RB {
        string_wrap* sw = $2;
        $$ = new term_func(sw->get(), $3->get());
        delete sw;
        delete $3;
    }
    | literal { $$ = $1; }
    | symbol {
        string_wrap* sw = $1;
        $$ = new term_symbol(sw->get());
        delete sw;
    }
    | let_term { $$ = $1; }
    ;

term_list
    : { $$ = new list_wrap<term>(); }
    | term term_list {
        $2->add(to_shared<term>($1));
        $$ = $2;
    }
    ;

let_clause
    : LB symbol sort_expr term RB {
        string_wrap* sw = $2;
        $$ = new let_term_item(sw->get(), to_shared<sort>($3), to_shared<term>($4));
        delete sw;
    }
    ;

let_clause_list_non
    : let_clause {
        $$ = new list_wrap<let_term_item>();
        $$->add(to_shared<let_term_item>($1));
    }
    | let_clause let_clause_list_non {
        $2->add(to_shared<let_term_item>($1));
        $$ = $2;
    }
    ;

let_term
    : LB LET LB let_clause_list_non RB term RB {
        $$ = new term_let($4->get(), to_shared<term>($6));
        delete $4;
    }
    ;

gterm
    : LB symbol gterm_list RB {
        string_wrap* sw = $2;
        list_wrap<term>* lw = $3;
        $$ = new term_func(sw->get(), lw->get());
        delete sw;
        delete lw;
    }
    | literal { $$ = $1; }
    | symbol {
        string_wrap* sw = $1;
        $$ = new term_symbol(sw->get());
        delete sw;
    }
    | let_gterm { $$ = $1; }
    | LB EXP_CONSTANT sort_expr RB {
        $$ = new term_exp(term_exp::term_exp_type::Constant, to_shared<sort>($3));
    }
    | LB EXP_VARIABLE sort_expr RB {
        $$ = new term_exp(term_exp::term_exp_type::Variable, to_shared<sort>($3));
    }
    | LB EXP_INPUT_VARIABLE sort_expr RB {
        $$ = new term_exp(term_exp::term_exp_type::InputVariable, to_shared<sort>($3));
    }
    | LB EXP_LOCAL_VARIABLE sort_expr RB {
        $$ = new term_exp(term_exp::term_exp_type::LocalVariable, to_shared<sort>($3));
    }
    ;

gterm_list
    : { $$ = new list_wrap<term>(); }
    | gterm gterm_list {
        $2->add(to_shared<term>($1));
        $$ = $2;
    }
    ;

let_gclause
    : LB symbol sort_expr gterm RB {
        string_wrap* sw = $2;
        $$ = new let_term_item(sw->get(), to_shared<sort>($3), to_shared<term>($4));
        delete sw;
    }
    ;

let_gclause_list_non
    : let_gclause {
        $$ = new list_wrap<let_term_item>();
        $$->add(to_shared<let_term_item>($1));
    }
    | let_gclause let_gclause_list_non {
        $2->add(to_shared<let_term_item>($1));
        $$ = $2;
    }
    ;

let_gterm
    : LB LET LB let_gclause_list_non RB gterm RB {
        $$ = new term_let($4->get(), to_shared<term>($6));
        delete $4;
    }
    ;

param
    : LB symbol sort_expr RB {
        string_wrap* sw = $2;
        $$ = new param(sw->get(), to_shared<sort>($3));
        delete sw;
    }
    ;

param_list
    : { $$ = new list_wrap<param>(); }
    | param param_list {
        $2->add(to_shared<param>($1));
        $$ = $2;
    }
    ;

gterm_list_non
    : gterm {
        $$ = new list_wrap<term>();
        $$->add(to_shared<term>($1));
    }
    | gterm gterm_list_non {
        $2->add(to_shared<term>($1));
        $$ = $2;
    }
    ;

ntdef
    : LB symbol sort_expr LB gterm_list_non RB RB {
        $$ = new synth_rule($2->get(), to_shared<sort>($3), $5->get());
        delete $2;
        delete $5;
    }
    ;

ntdef_list_non
    : ntdef {
        $$ = new list_wrap<synth_rule>();
        $$->add(to_shared<synth_rule>($1));
    }
    | ntdef ntdef_list_non {
        $2->add(to_shared<synth_rule>($1));
        $$ = $2;
    }
    ;

cmd_set_logic
    : LB CMD_SET_LOGIC symbol RB {
        $$ = new cmd_set_logic($3->get());
        delete $3;
    }
    ;

cmd_define_sort
    : LB CMD_DEFINE_SORT symbol sort_expr RB {
        $$ = new cmd_define_sort($3->get(), to_shared<sort>($4));
        delete $3;
    }
    ;

cmd_declare_var
    : LB CMD_DECLARE_VAR symbol sort_expr RB {
        $$ = new cmd_declare_var($3->get(), to_shared<sort>($4));
        delete $3;
    }
    ;

cmd_declare_fun
    : LB CMD_DECLARE_FUN symbol LB sort_expr_list RB sort_expr RB {
        $$ = new cmd_declare_fun($3->get(), $5->get(), to_shared<sort>($7));
        delete $3;
        delete $5;
    }
    ;

cmd_define_fun
    : LB CMD_DEFINE_FUN symbol LB param_list RB sort_expr term RB {
        $$ = new cmd_define_fun($3->get(), $5->get(), to_shared<sort>($7), to_shared<term>($8));
        delete $3;
        delete $5;
    }
    ;

cmd_synth_fun
    : LB CMD_SYNTH_FUN symbol LB param_list RB sort_expr LB ntdef_list_non RB RB {
        $$ = new cmd_synth_fun($3->get(), $5->get(), to_shared<sort>($7), $9->get());
        delete $3;
        delete $5;
        delete $9;
    }
    ;

cmd_constraint
    : LB CMD_CONSTRAINT term RB {
        $$ = new cmd_constraint(to_shared<term>($3));
    }
    ;

cmd_check_synth
    : LB CMD_CHECK_SYNTH RB {
        $$ = new cmd_check_synth();
    }
    ;

option
    : LB symbol string RB {
        $$ = new option($2->get(), $3->get());
        delete $2;
        delete $3;
    }
    ;

option_list_non
    : option {
        $$ = new list_wrap<option>();
        $$->add(to_shared<option>($1));
    }
    | option option_list_non {
        $2->add(to_shared<option>($1));
        $$ = $2;
    }
    ;

cmd_set_options
    : LB CMD_SET_OPTIONS LB option_list_non RB RB {
        $$ = new cmd_set_options($4->get());
        delete $4;
    }
    ;

%%
inline void sygusparser::parser::error (const std::string& msg)
{
    throw std::runtime_error(msg);
}
