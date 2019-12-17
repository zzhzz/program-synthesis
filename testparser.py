
import sygusparser
import sygussolver

cmds = sygusparser.parser.parse(open('open_tests/test.sl').read())
solver = sygussolver.SygusSolver()
graph = solver.solve(cmds)
rulemapping = graph.rule_mapping



if __name__ == '__main__':
    pass