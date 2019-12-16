
import sygusparser
import sygussolver

import os

INPUT_DIR = 'open_tests'

# files = sorted(os.listdir(INPUT_DIR))
files = ['max2.sl', 'three.sl', 'tutorial.sl']
for fname in files:
    cmds = sygusparser.parser.parse(open(os.path.join(INPUT_DIR, fname)).read())
    print(fname)
    # if cmds.cmd_set_logic:
    #     print(cmds.cmd_set_logic)
    # for cmd in cmds.cmd_list:
    #     print(cmd)
    # print()
    solver = sygussolver.SygusSolver()
    solver.solve(cmds)

