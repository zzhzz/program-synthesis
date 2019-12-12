
#include "sygusparser_lexer.hh"
#include "sygusparser.y.hh"

int main(int argc, char* argv[])
{
    sygusparser::sygusparser_lexer lexer;
    sygusparser::parser parser{lexer};
    parser.parse();
    return 0;
}
