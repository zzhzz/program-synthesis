
#include "sygusparser_lexer.hh"
#include "sygusparser.y.hh"
#include "tree.h"



int main(int argc, char* argv[])
{
    sygus_command_list cmds;
    sygusparser::sygusparser_lexer lexer;
    sygusparser::parser parser{lexer, cmds};
    parser.parse();
    return 0;
}
