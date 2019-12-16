
import sygusparser
import sygussolver

import os

INPUT_DIR = 'open_tests'

files = sorted(os.listdir(INPUT_DIR))
for fname in files:
    cmds = sygusparser.parser.parse(open(os.path.join(INPUT_DIR, fname)).read())
    solver = sygussolver.SygusSolver()
    solver.solve(cmds)

