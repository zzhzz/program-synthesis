
import sygusparser
import sygussolver

import os
import time

INPUT_DIR = 'open_tests'

# files = sorted(os.listdir(INPUT_DIR))
files = ['max2.sl', 'three.sl', 'tutorial.sl']
for fname in files:
    print(fname)
    time0 = time.time()
    cmds = sygusparser.parser.parse(open(os.path.join(INPUT_DIR, fname)).read())
    time1 = time.time()
    solver = sygussolver.SygusSolver()
    solver.solve(cmds)
    time2 = time.time()
    print(f'Total: {time2-time0:.04f}s. Parse: {time1-time0:.04f}s. Solve: {time2-time1:.04f}s.')
