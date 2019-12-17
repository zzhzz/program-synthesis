import torch as th
import torch.nn as nn
import torch.nn.functional as F

from sygustree import ExprType


class RecursiveDecoder(nn.Module):
    def __init__(self, hiddens, reward_lstm=None):
        super(RecursiveDecoder, self).__init__()
        self.hid = hiddens
        self.reward_lstm = reward_lstm
        self.state_gru = nn.GRUCell(self.hid, self.hid)

        self.value_net = nn.Sequential(
            nn.Linear(self.hid, self.hid),
            nn.ReLU(),
            nn.Linear(self.hid, self.hid)
        )

        self.first_attn = nn.Linear(self.hid, 1)
        self.tree_encoder = None
        self.state = None

    def reset(self):
        self.state = None

    def forward(self, env, graph_emb, use_random, eps=0.05):
        if env.t == 0:
            # attention for first cell
            weights = F.softmax(self.first_attn(graph_emb))
            self.state = th.sum(weights * graph_emb, dim=0, keepdim=True)

        value = self.value_net(self.state)
        self.nll = 0.0
        extend_item = env.expand_ls.pop(0)
        cfg_mapping = env.cfg_mapping
        act_space = cfg_mapping[extend_item][1]
        avalid_act_embedding = graph_emb[act_space]

        if len(avalid_act_embedding) == 1:
            # one choice
            avalid_act_embedding = avalid_act_embedding.unsqueeze(0)

        act = self.choose_action(self.state, avalid_act_embedding, use_random, eps)
        act_emb = th.index_select(avalid_act_embedding, 0, act)

        self.state = self.state_gru(act_emb, self.state)

        act_ind = act.cpu().item()
        prod_rules = env.cfg_mapping[extend_item][1]
        rule = env.rule_list[prod_rules[act_ind]]
        if rule.type == ExprType.Func:
            args_ls = list(rule.children) if rule.children is not None else []
            args = [r.name for r in args_ls]
            env.action = [rule.name] + args
        else:
            env.action = rule.value
        args_ls = list(rule.children) if rule.children is not None else []
        argname_ls = [r.name for r in args_ls]
        env.expand_ls = argname_ls + env.expand_ls
        return self.nll, value


    def choose_action(self, state, cls_w, use_random, eps):
        logits = F.linear(state, cls_w, None)

        ll = F.log_softmax(logits)
        if use_random:
            scores = th.exp(ll) * (1. - eps) + eps / ll.shape[1]
            picked = th.multinomial(scores, 1)
        else:
            _, picked = th.max(ll, 1)

        picked = picked.view(1)
        self.nll += F.nll_loss(ll, picked) # same as cross entropy
        return picked






