import torch as th
import torch.nn as nn
import dgl.function as fn
import math

class TBCNN(nn.Module):
    def __init__(self, token_size, feature_size, conv_size):
        super(TBCNN, self).__init__()
        self.emb = nn.Embedding(token_size, feature_size)
        self.token_size = token_size
        self.feature_size = feature_size
        self.conv_out = conv_size
        self.message_func = fn.src_mul_edge(src='h', edge='eta', out='h')
        self.reduce_func = fn.sum(msg='h', out='h')
        self.W = nn.Parameter(th.FloatTensor(feature_size, 3*conv_size))
        self.bias = nn.Parameter(th.FloatTensor(conv_size))
        nn.init.xavier_normal_(self.W)
        std = 1./math.sqrt(conv_size)
        self.bias.data.uniform_(-std, std)
        self.mlp = nn.Linear(conv_size, 1)

    def forward(self, ast):
        tokens = ast.ndata['token']
        fea = self.emb(tokens)
        ast.ndata.update({'h': th.matmul(fea, self.W).view(-1, 3, self.conv_out)})
        ast.update_all(self.message_func, self.reduce_func)
        conv_out = th.tanh(th.sum(ast.ndata.pop('h'), dim=1) + self.bias)
        return th.mean(conv_out)


