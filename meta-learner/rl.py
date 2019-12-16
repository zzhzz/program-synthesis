import torch as th
import torch.nn.functional as F
import numpy as np
from ggnn import GGNN

class RLEnv:
    def __init__(self, samples):
        raise NotImplementedError

    def is_done(self):
        pass



def rollout(sample, graph_embedding, decoder, rudder, previous_avg_return, num_episode, use_random, eps):

    total_loss, rudder_loss, best_reward, best_tree, acc_reward = 0.0, 0.0, -5.0, None, 0.0

    for episode_id in range(num_episode):
         NLL_list, value_list, reward_list = [], [], []

         env = RLEnv(sample)
         decoder.reset()
         rudder.reset()

         while not env.is_done():
            nll, val = decoder(env, graph_embedding, use_random, eps)

