
extern "C"
{
#include "y.tab.h"
}

int main(int argc, char* argv[])
{
    yyparse();
    return 0;
}