import numpy as np
import json
import dgl
import torch as th
import torch.nn as nn
from RL.tbcnn import TBCNN


class Value:
    def __init__(self, token_map, alpha):
        self.weights = TBCNN(20, 5, 10)
        self.loss = nn.MSELoss()
        self.optim = th.optim.Adam(self.weights.parameters(), lr=alpha)
        self.token_map = token_map

    def hash(self, program):
        g = dgl.DGLGraph()
        edges, nodes = [], ['My-Start-Symbol']
        depthes = [0]
        def dfs(program, u, dep):
            for i, item in enumerate(program):
                if type(item) == list:
                    if item[0] in ['+', '-', 'ite']:
                        label = 'Start'
                    else:
                        label = 'StartBool'
                    idx = len(nodes)
                    edges.append((u, idx))
                    nodes.append(label)
                    depthes.append(dep)
                    dfs(item, idx, dep + 1)
                else:
                    idx = len(nodes)
                    edges.append((u, idx))
                    nodes.append(item)
                    depthes.append(dep + 1)
        dfs(program, 0, 0)
        for idx, node in enumerate(nodes):
            nodes[idx] = self.token_map[node]
        g.add_nodes(len(nodes))
        g.ndata['token'] = th.LongTensor(th.from_numpy(np.array(nodes)))
        ast_edges = np.array(edges)
        g.add_edges(ast_edges[:, 1], ast_edges[:, 0])
        etas = [[] for _ in range(len(ast_edges))]
        ast_g = [[] for _ in range(len(nodes))]
        for eid, edge in enumerate(edges):
            u, v = edge
            ast_g[u].append((v, eid))
        for u in range(len(nodes)):
            c = len(ast_g[u])
            for i, item in enumerate(ast_g[u]):
                v, eid = item
                eta_t = th.FloatTensor([float(depthes[v] - depthes[u]) / 2.0])
                if c > 1:
                    eta_r = th.FloatTensor([float(i)/c * (1.0 - eta_t)])
                    eta_l = th.FloatTensor([(float(c) - float(i))/c * (1.0 - eta_t)])
                elif c == 1:
                    eta_l = th.FloatTensor([0.5 * (1 - eta_t)])
                    eta_r = th.FloatTensor([0.5 * (1 - eta_t)])
                etas[eid] = th.cat([eta_t, eta_l, eta_r]).view(1, 3, 1)
        g.edata['eta'] = th.cat(etas, dim=0)
        return g

    def get_value(self, program):
        return self.weights(self.hash(program)).item()

    def update_value(self, program, returns):
        estimate = self.weights(self.hash(program))
        loss = self.loss(estimate.view(-1, 1), th.FloatTensor([returns]).view(-1, 1))
        self.optim.zero_grad()
        loss.backward()
        self.optim.step()


def get_possible_next(Stmts, produtions, depth):
    a_list = []
    if depth >= 10:
        return a_list, -1
    for index in range(len(Stmts)):
        if type(Stmts[index]) == list:
            try_actions, flag = get_possible_next(Stmts[index], produtions, depth+1)
            if flag == -1:
                return [], -1
            if len(try_actions) > 0:
                for act in try_actions:
                    act = json.loads(act)
                    new_program = Stmts[0:index] + [act] + Stmts[index + 1:]
                    a_list.append(json.dumps(new_program))
        elif Stmts[index] in produtions:
            for act in produtions[Stmts[index]]:
                new_program = Stmts[0:index] + [act] + Stmts[index + 1:]
                a_list.append(json.dumps(new_program))
        if len(a_list) > 0:
            return a_list, 0
    return a_list, 0


def calc_depth(program, depth):
    dep = depth
    for index in range(len(program)):
        if type(program[index]) == list:
            dep = max(calc_depth(program[index], depth+1), dep)
    return dep

class Agent:
    def __init__(self, productions, env, token_map, alpha=0.1, eps=.1):
        self.actions = productions
        self.eps = eps
        self.alpha = alpha
        self.env = env
        self.values = Value(token_map, alpha)

    def action(self, curr_program):
        next_list, flag = get_possible_next(curr_program, self.actions, 0)
        if len(next_list) == 0 or flag == -1:
            return curr_program
        if np.random.binomial(1, self.eps) == 1:
            return json.loads(np.random.choice(next_list))
        else:
            vals = []
            for item in next_list:
                new_rule = json.loads(item)
                vals.append(self.values.get_value(new_rule))
            return json.loads(next_list[np.random.choice(np.flatnonzero(np.array(vals) == np.max(vals)))])

    def returns(self, program, epoch):
        nxt_prgm, flag = get_possible_next(program, self.actions, 0)
        if flag == -1:
            return -1, True
        if len(nxt_prgm) == 0:
            dep = calc_depth(program, 0)
            return self.env.rewards(program, dep, epoch), True
        return 0, False




