
#include "sygusparser_lexer.hh"
#include "sygusparser.y.hh"
#include "tree.h"

int main(int argc, char *argv[])
{
    sygus_command_list cmds;
    sygusparser::sygusparser_lexer lexer;
    sygusparser::parser parser{lexer, cmds};
    parser.parse();
    cmds.finish();

    std::cout << "finished\n";
    if (cmds.setlogic.get())
        std::cout << *cmds.setlogic << std::endl;
    for (auto &c : cmds.cmds)
        std::cout << *c << std::endl;

    return 0;
}
