
import os
import sys

import __main__

path, fname = os.path.split(__main__.__file__)

os.execve(
    '/bin/bash',
    ('/bin/bash', path + '/' + 'mainscript.bash', path, sys.argv[1]),
    {}
)
