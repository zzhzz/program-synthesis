#ifndef sygusparser_lexer_header
#define sygusparser_lexer_header

#if ! defined(yyFlexLexerOnce)
#undef yyFlexLexer
#define yyFlexLexer sygusparser_FlexLexer // the trick with prefix; no namespace here :(
#include <FlexLexer.h>
#endif

#undef YY_DECL
#define YY_DECL int sygusparser::sygusparser_lexer::get_next_token()

namespace sygusparser
{
    class sygusparser_lexer: public sygusparser_FlexLexer
    {
    public:
        int get_next_token();
    };
}

#endif
