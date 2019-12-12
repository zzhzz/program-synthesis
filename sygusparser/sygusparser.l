
SYMBOLBEGIN [_\+\-\*&\|!~<>=/%\?\.\$\^a-zA-Z0-9]
SYMBOLDETAIL [_\+\-\*&\|!~<>=/%\?\.\$\^a-zA-Z]

INTVAL [0-9]
WHITESPACE [ \r\n\t]

%{

%}

%%

";.+" {}
"{WHITESPACE}+" {}

"\(" { return LB; }
"\)" { return RB; }

"true" { return BOOL_TRUE; }
"false" { return BOOL_FALSE; }

"Int" { return SORT_INT; }
"Bool" { return SORT_BOOL; }

"let" { return LET; }

"set-logic" { return CMD_SET_LOGIC; }
"define-sort" { return CMD_DEFINE_FUN; }
"declare-var" { return CMD_DECLARE_VAR; }
"declare-fun" { return CMD_DECLARE_FUN; }
"define-fun" { return CMD_DEFINE_FUN; }
"synth-fun" { return CMD_SYNTH_FUN; }
"constraint" { return CMD_CONSTRAINT; }
"check-synth" {return CMD_CHECK_SYNTH; }
"set-options" { return CMD_SET_OPTIONS; }

"Constant" { return EXP_CONSTANT; }
"Variable" { return EXP_VARIABLE; }
"InputVariable" { return EXP_INPUT_VARIABLE; }
"LocalVariable" { return EXP_LOCAL_VARIABLE; }

"-?[0-9]" { return INT; }
"\"[^\"]*\"" { return STRING; }

"{SYMBOLBEGIN}{SYMBOLDETAIL}*" { return SYMBOL; }


%%

