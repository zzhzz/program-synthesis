
import sygusparser
import sygussolver

cmds = sygusparser.parser.parse(open('../open_tests/max2.sl').read())
solver = sygussolver.SygusSolver()
graph = solver.solve(cmds)
rulemapping = graph.rule_mapping
# rule_list

print(graph.nodes)
print(graph.rule_mapping)
print(graph.rule_list)
print(graph.edges)


if __name__ == '__main__':
    pass