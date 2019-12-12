import sexp
import sys
import time
import z3
from RL.agent import Agent
from RL.env import Enviroment


def stripComments(bmFile):
    noComments = '('
    for line in bmFile:
        line = line.split(';', 1)[0]
        noComments += line
    return noComments + ')'


epoch = 10000
gamma = .8

if __name__ == '__main__':
    timeStart = time.time()
    token_map = {
        'x': 0,
        'y': 1,
        'z': 2,
        '0': 3,
        '1': 4,
        'Start': 5,
        '+': 6,
        '-': 7,
        'ite': 8,
        'StartBool': 9,
        'and': 10,
        'or': 11,
        'not': 12,
        '<=': 13,
        '>=': 14,
        '=': 15,
        'My-Start-Symbol': 16
    }
    benchmarkFile = open(sys.argv[1])
    bm = stripComments(benchmarkFile)
    bmExpr = sexp.sexp.parseString(bm, parseAll=True).asList()[0] #Parse string to python list
    SynFunExpr = []
    StartSym = 'My-Start-Symbol'
    for expr in bmExpr:
        if len(expr) == 0:
            continue
        elif expr[0] == 'synth-fun':
            SynFunExpr = expr
    FuncDefine = ['define-fun']+SynFunExpr[1:4] #copy function signature

    Productions = {StartSym:[]}
    Type = {StartSym:SynFunExpr[3]} # set starting symbol's return type

    for NonTerm in SynFunExpr[4]: #SynFunExpr[4] is the production rules
        NTName = NonTerm[0]
        NTType = NonTerm[1]
        if NTType == Type[StartSym]:
            Productions[StartSym].append(NTName)
        Type[NTName] = NTType
        Productions[NTName] = []
        for NT in NonTerm[2]:
            if type(NT) == tuple:
                Productions[NTName].append(str(NT[1])) # deal with ('Int',0). You can also utilize type information, but you will suffer from these tuples.
            else:
                Productions[NTName].append(NT)

    Env = Enviroment(bmExpr, FuncDefine)
    agent = Agent(Productions, Env, token_map)

    for epoch_id in range(epoch):
        print(f'Epoch {epoch_id}')
        program = [StartSym]
        count = 0
        action_program = agent.action(program)
        stop_flag = False
        while True:
            count += 1
            try:
                rewards, stop_flag = agent.returns(action_program, epoch_id)
            except z3.z3types.Z3Exception as e:
                rewards = -10
                stop_flag = True
            next_program = agent.action(action_program)
            returns = rewards + gamma * agent.values.get_value(next_program)
            agent.values.update_value(program, returns)
            if stop_flag:
                agent.values.update_value(action_program, returns)
                break
            program = action_program
            action_program = next_program
    print(f'Time: {time.time() - timeStart}s', file=sys.stderr)
    print("Result: " + Env.result)

