import torch as th
import torch.nn as nn
import torch.nn.functional as F
import dgl
import dgl.function as fn

class GGNN(nn.Module):
    def __init__(self, tokens, hiddens, edge_types, steps):
        super(GGNN, self).__init__()
        self.tokens = tokens
        self.state_dim = hiddens
        self.edge_type = edge_types
        self.n_step = steps
        self.emb = nn.Embedding(tokens, self.state_dim)
        self.fc_weights = nn.Embedding(edge_types, self.state_dim * self.state_dim * 2)
        self.edge_message = fn.src_mul_edge(src='h', edge='e_w', out='h')
        self.message_func = fn.copy_edge(edge='h', out='h')
        self.reduce_func = fn.sum(msg='h', out='h')
        self.reset_gate = nn.Sequential(
            nn.Linear(self.state_dim * 3, self.state_dim),
            nn.Sigmoid()
        )
        self.update_gate = nn.Sequential(
            nn.Linear(self.state_dim * 3, self.state_dim),
            nn.Sigmoid()
        )
        self.trans = nn.Sequential(
            nn.Linear(self.state_dim * 3, self.state_dim),
            nn.Tanh()
        )

    def forward(self, g):
        prop_state = self.emb(g.ndata['token'])
        edge_weight = self.fc_weights(g.edata['type']).view(-1, self.state_dim, self.state_dim, 2)
        g.edata.update({
            'e_w': edge_weight.view(-1, self.state_dim, self.state_dim * 2)
        })
        rev_g = g.reverse(share_edata=True, share_ndata=True)
        for i in range(self.n_step):
            g.ndata.update({
                'h': prop_state.view(-1, self.state_dim, 1)
            })
            g.apply_edges(self.edge_message)
            fea = g.edata.pop('h').sum(dim=1).view(-1, self.state_dim, 2)
            g.edata.update({
                'h': fea[:, :, 0]
            })
            g.update_all(self.message_func, self.reduce_func)
            in_fea = g.ndata.pop('h').view(-1, self.state_dim)
            rev_g.edata.update({
                'h': fea[:, :, 1]
            })
            rev_g.update_all(self.message_func, self.reduce_func)
            out_fea = rev_g.ndata.pop('h').view(-1, self.state_dim)
            fea = th.cat([in_fea, out_fea, prop_state], dim=1).view(-1, self.state_dim * 3)

            r = self.reset_gate(fea)
            z = self.update_gate(fea)
            cat_input = th.cat([in_fea, out_fea, r * prop_state], dim=1)
            h_hat = self.trans(cat_input)

            prop_state = (1. - z) * prop_state + z * h_hat
        g.edata.pop('e_w')
        g.edata.pop('h')
        return prop_state
