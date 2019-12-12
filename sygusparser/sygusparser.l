%option nodefault
%option noyywrap
%option c++
%option yyclass="sygusparser_lexer"
%option prefix="sygusparser_"

SYMBOLBEGIN [_\+\-\*&\|!~<>=/%\?\.\$\^a-zA-Z]
SYMBOLDETAIL [_\+\-\*&\|!~<>=/%\?\.\$\^a-zA-Z0-9]

INTVAL [0-9]
WHITESPACE [ \r\n\t]

QUOTE \"
NONQUOTE [^"]

DIGITAL [0-9]
MINUS -

%{
#include <iostream>
using std::cin;
using std::cout;
using std::cerr;

#include "sygusparser_lexer.hh"
#include "sygusparser.y.hh"
%}

%%

";".+ {}
{WHITESPACE}+ {}

"(" { return sygusparser::parser::token::LB; }
")" { return sygusparser::parser::token::RB; }

"true" { return sygusparser::parser::token::BOOL_TRUE; }
"false" { return sygusparser::parser::token::BOOL_FALSE; }

"Int" { return sygusparser::parser::token::SORT_INT; }
"Bool" { return sygusparser::parser::token::SORT_BOOL; }

"let" { return sygusparser::parser::token::LET; }

"set-logic" { return sygusparser::parser::token::CMD_SET_LOGIC; }
"define-sort" { return sygusparser::parser::token::CMD_DEFINE_SORT; }
"declare-var" { return sygusparser::parser::token::CMD_DECLARE_VAR; }
"declare-fun" { return sygusparser::parser::token::CMD_DECLARE_FUN; }
"define-fun" { return sygusparser::parser::token::CMD_DEFINE_FUN; }
"synth-fun" { return sygusparser::parser::token::CMD_SYNTH_FUN; }
"constraint" { return sygusparser::parser::token::CMD_CONSTRAINT; }
"check-synth" {return sygusparser::parser::token::CMD_CHECK_SYNTH; }
"set-options" { return sygusparser::parser::token::CMD_SET_OPTIONS; }

"Constant" { return sygusparser::parser::token::EXP_CONSTANT; }
"Variable" { return sygusparser::parser::token::EXP_VARIABLE; }
"InputVariable" { return sygusparser::parser::token::EXP_INPUT_VARIABLE; }
"LocalVariable" { return sygusparser::parser::token::EXP_LOCAL_VARIABLE; }

{MINUS}?{DIGITAL}+ { return sygusparser::parser::token::INT; }
{QUOTE}{NONQUOTE}*{QUOTE} { return sygusparser::parser::token::STRING; }
{SYMBOLBEGIN}{SYMBOLDETAIL}* { return sygusparser::parser::token::SYMBOL; }

%%
