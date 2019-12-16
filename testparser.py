
import sygusparser
import sygussolver

cmds = sygusparser.parser.parse(open('open_tests/test.sl').read())
solver = sygussolver.SygusSolver()
graph = solver.solve(cmds)
