import torch as th
import torch.nn.functional as F
import numpy as np
from ggnn import GGNN
from checker import Checker
from collections import deque


class RLEnv:
    def __init__(self, samples, expr):
        self.graph = samples
        self.t = 0
        self.r = None
        self.tree = ['Start']
        self.checker = Checker(expr)
        self.expand_ls = ['Start']
        self.action = None
        self.cfg_mapping = samples.rule_mapping
        self.rule_list = samples.rule_list
        self.nonterm_list = {}
        for key in samples.non_terminal_list:
            self.nonterm_list[samples.non_terminal_list[key]] = key

    def step(self):
        if self.action is not None:
            def Expand(tree, dep):
                depth = dep
                new_tree = None
                for idx, item in enumerate(tree):
                    if isinstance(item, list):
                        expand, d = Expand(item, dep+1)
                        depth = max(depth, d)
                        if expand is not None:
                            new_tree = tree[0:idx] + [expand] + tree[idx+1:]
                    elif item in self.nonterm_list.keys():
                        new_tree = tree[0:idx] + [self.action] + tree[idx+1:]
                    if new_tree is not None:
                        return new_tree, depth
                return new_tree, depth

            ntree, dep = Expand(self.tree, 0)
            if dep >= 10:
                self.r = -1.0
                self.expand_ls = []
            if ntree is None:
                raise ValueError
            self.tree = ntree
        else:
            raise ValueError

    def is_done(self):
        return len(self.expand_ls) == 0

    def reset(self):
        self.t = 0
        self.r = None
        self.tree = ['Start']

    def rewards(self):
        if self.is_done():
            if self.r is None:
                return self.checker.check(self.tree, self.t)
            else:
                return self.r
        else:
            return 0.0




def rollout(expr, sample, graph_embedding, decoder, rudder, previous_avg_return, num_episode, use_random, eps):
    total_loss, rudder_loss, best_reward, best_tree, acc_reward = 0.0, 0.0, -5.0, None, 0.0
    for episode_id in range(num_episode):
        NLL_list, value_list, reward_list = [], [], []

        env = RLEnv(sample, expr)
        decoder.reset()
        while not env.is_done():
            nll, val = decoder(env, graph_embedding, use_random, eps)
            env.step()
            reward = env.rewards()
            NLL_list.append(nll)
            value_list.append(val)
            reward_list.append(reward)
            env.t += 1
        true_return = np.sum(reward_list)
        policy_loss, val_loss = a2c_loss(NLL_list, value_list, reward_list)
        total_loss += policy_loss + val_loss

        if true_return > best_reward:
            best_reward = true_return
            best_tree = env.tree
        acc_reward += true_return

    total_loss /= num_episode
    rudder_loss /= num_episode
    acc_reward /= num_episode

    return total_loss, rudder_loss, best_reward, best_tree, acc_reward



def a2c_loss(nll_list, value_list, reward_list):
    r = 0.0
    rewards = []
    # accumlated future reward
    for t in range(len(reward_list) - 1, -1, -1):
        r += reward_list[t]
        rewards.insert(0, r / 10.0)

    policy_loss = 0.0
    targets = []
    for t in range(len(reward_list)):
        adv = rewards[t] - value_list[t].data[0, 0]
        policy_loss += nll_list[t] * adv
        targets.append(th.FloatTensor([[rewards[t]]], ).requires_grad_())

    policy_loss /= len(reward_list)
    value_pred = th.cat(value_list, dim=0)
    targets = th.cat(targets, dim=0)
    value_loss = F.mse_loss(value_pred, targets)

    return policy_loss, value_loss



