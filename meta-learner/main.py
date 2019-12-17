import os
import sys
import dgl
import sygusparser
import numpy as np
import torch as th
from rl import rollout
import torch.nn as nn

from ggnn import GGNN
from itertools import chain
from decoder import RecursiveDecoder
from sygussolver import SygusGraph, SygusSolver

def build_graph(graph):
    g = dgl.DGLGraph()
    g.add_nodes(len(graph.nodes))
    g.ndata['token'] = th.LongTensor(th.from_numpy(np.array(graph.nodes).astype(np.long)))
    edges = np.array(graph.edges).reshape(-1, 3)
    g.add_edges(edges[:, 1], edges[:, 0])
    g.edata['type'] = th.LongTensor(th.from_numpy(np.array(edges[:, 2]).astype(np.long)))
    return g





def main():
    hid_dim = 100
    EPOCH = 10
    EPS = .85
    DECAY = .9999


    with open('../open_tests/max2.sl', 'r') as fh:
        problem = sygusparser.parser.parse(fh.read())
        solver = SygusSolver()
        graph = solver.solve(problem)
    G = build_graph(graph)
    graph_emb = GGNN(tokens=1000, hiddens=hid_dim, edge_types=6, steps=3)
    decoder = RecursiveDecoder(hiddens=hid_dim)

    params = [graph_emb.parameters(), decoder.parameters()]

    opt = th.optim.Adam(chain.from_iterable(params), lr=0.001)

    for epoch in range(EPOCH):
        epoch_best_reward = -5.0
        epoch_best_root = None
        epoch_acc_reward = 0.0

        for k in range(100):
            gemb = graph_emb(G)
            total_loss, rudder_loss, best_reward, best_tree, acc_reward = rollout(graph, gemb, decoder, None,
                                                                                  (epoch_acc_reward / (k + 1)),
                                                                                  num_episode=10,
                                                                                  use_random=True, eps=EPS)
            EPS *= DECAY

            epoch_acc_reward += acc_reward
            if best_reward > epoch_best_reward:
                epoch_best_reward = best_reward
                epoch_best_root = best_tree

            opt.zero_grad()
            loss = total_loss
            loss.backward()
            opt.step()
            print('Avg reward: %.4f'% (epoch_acc_reward / (k+1)))






if __name__ == '__main__':
    main()
