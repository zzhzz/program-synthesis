
import sygusparser
import sygussolver

import os
import time
import sygusmodel

INPUT_DIR = 'open_tests'

files = sorted(os.listdir(INPUT_DIR))

# ignores = [
#     'max_11.sl', 'max12.sl', 'max13.sl', 'max14.sl', 'max15.sl'
# ]

# files = ['max2.sl', 'max3.sl', 'max4.sl', 'max5.sl', 'max6.sl', 'max7.sl']
# files = ['array_search_2.sl', 'array_search_3.sl', 'array_search_4.sl', 'array_search_5.sl', 'array_search_6.sl', 'array_search_7.sl']
files = ['s1.sl']
# files = ['s2.sl']
# files = ['s3.sl']
# files = ['three.sl']
# files = ['tutorial.sl']

neural = sygusmodel.SygusNetwork()

for fname in files:
    # if fname in ignores:
    #     continue
    print(fname)
    time0 = time.time()
    cmds = sygusparser.parser.parse(open(os.path.join(INPUT_DIR, fname)).read())
    time1 = time.time()
    solver = sygussolver.SygusSolver(neural)
    solver.filename = fname
    solver.solve(cmds,)
    time2 = time.time()
    print(f'Total: {time2-time0:.04f}s. Parse: {time1-time0:.04f}s. Solve: {time2-time1:.04f}s.')

import os
os._exit(0)
