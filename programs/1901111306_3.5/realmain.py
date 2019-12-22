import sygusparser
import sygussolver

import sys
import os
import time
import sygusmodel

fname = sys.argv[1]
_, shortfname = os.path.split(fname)

neural = sygusmodel.SygusNetwork()

time0 = time.time()
cmds = sygusparser.parser.parse(open(fname).read())
time1 = time.time()
solver = sygussolver.SygusSolver(neural)
solver.filename = shortfname
solver.solve(cmds)
time2 = time.time()
print(
    f"Total: {time2-time0:.04f}s. Parse: {time1-time0:.04f}s. Solve: {time2-time1:.04f}s.",
    file=sys.stderr
)
sys.stdout.flush()
os._exit(0)
