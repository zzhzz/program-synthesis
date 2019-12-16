import torch as th
import torch.nn.functional as F
import numpy as np
from ggnn import GGNN
from checker import Checker

class RLEnv:
    def __init__(self, samples):
        self.t = 0
        self.tree = None
        self.checker = Checker()
        self.action_ls = [()]

    def is_done(self):
        pass

    def reset(self):
        self.t = 0
        self.tree = None

    def rewards(self):
        pass




def rollout(sample, graph_embedding, decoder, rudder, previous_avg_return, num_episode, use_random, eps):
    total_loss, rudder_loss, best_reward, best_tree, acc_reward = 0.0, 0.0, -5.0, None, 0.0
    for episode_id in range(num_episode):
        NLL_list, value_list, reward_list = [], [], []

        env = RLEnv(sample)
        decoder.reset()
        # rudder.reset()
        while not env.is_done():
            nll, val = decoder(env, graph_embedding, use_random, eps)
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



