from z3 import Int, Bool, IntSort, BoolSort, Solver, And, Not, parse_smt2_file, parse_smt2_string, unsat, Function
verbose = False
import translator

def DeclareVar(sort, name):
    if sort == "Int":
        return Int(name)
    if sort == 'Bool':
        return Bool(name)


def getSort(sort):
    if sort == "Int":
        return IntSort()
    if sort == "Bool":
        return BoolSort()


def toString(Expr, Bracket=True, ForceBracket=False):
    if type(Expr) == str:
        return Expr
    if type(Expr) == tuple:
        return (str(Expr[1]))  # todo: immediate
    subexpr = []
    for expr in Expr:
        if type(expr) == list:
            subexpr.append(toString(expr, ForceBracket=ForceBracket))
        elif type(expr) == tuple:
            subexpr.append(str(expr[1]))
        else:
            subexpr.append(expr)

    if not Bracket:
        # print subexpr
        return "%s" % (' '.join(subexpr))
    # Avoid Redundant Brackets
    if ForceBracket:
        return "(%s)" % (' '.join(subexpr))
    if len(subexpr) == 1:
        return "%s" % (' '.join(subexpr))
    else:
        return "(%s)" % (' '.join(subexpr))


def ReadQuery(bmExpr):
    SynFunExpr = []
    VarDecMap = {}
    Constraints = []
    FunDefMap = {}
    for expr in bmExpr:
        if len(expr) == 0:
            continue
        elif expr[0] == 'synth-fun':
            SynFunExpr = expr
        elif expr[0] == 'declare-var':
            VarDecMap[expr[1]] = expr
        elif expr[0] == 'constraint':
            Constraints.append(expr)
        elif expr[0] == 'define-fun':
            FunDefMap[expr[1]] = expr

    if verbose:
        print(SynFunExpr)
        print(VarDecMap)
        print(FunDefMap)
        print(Constraints)

    VarTable = {}
    # Declare Var
    for var in VarDecMap:
        VarTable[var] = DeclareVar(VarDecMap[var][2], var)

    # Declare Target Function
    class SynFunction:
        def __init__(self, SynFunExpr):
            self.name = SynFunExpr[1]
            # TODO: arg and ret sort
            self.argList = SynFunExpr[2]
            self.retSort = SynFunExpr[3]
            self.Sorts = []
            for expr in self.argList:
                self.Sorts.append(getSort(expr[1]))
            self.Sorts.append(getSort(self.retSort))
            self.targetFunction = Function('__TARGET_FUNCTION__', *(self.Sorts))

    synFunction = SynFunction(SynFunExpr)

    class Checker:
        def __init__(self, VarTable, synFunction, Constraints):
            self.VarTable = VarTable
            self.synFunction = synFunction
            self.Constraints = Constraints
            self.solver = Solver()

        def check(self, funcDefStr):
            const = {}
            for idx, constraint in enumerate(Constraints):
                self.solver.push()
                spec_smt2 = [funcDefStr]
                spec_smt2.append('(assert %s)' % (toString(constraint[1:])))
                spec_smt2 = '\n'.join(spec_smt2)
                spec = parse_smt2_string(spec_smt2, decls=dict(self.VarTable))
                spec = And(spec)
                self.solver.add(Not(spec))
                if verbose:
                    print("spec:", spec)

                res = self.solver.check()
                if res == unsat:
                    self.solver.pop()
                else:
                    model = self.solver.model()
                    self.solver.pop()
                    const[idx] = model
            return const, len(Constraints)

    checker = Checker(VarTable, synFunction, Constraints)
    return checker, len(Constraints)


class Checker:
    def __init__(self, expr):
        self.pc = .7
        self.pm = .1
        self.n = 20
        self.checker, self.sz = ReadQuery(expr)
        self.ce_dict = [{} for _ in range(self.sz)]
        self.appear = [{} for _ in range(self.sz)]
        self.const_dict = [{} for _ in range(self.sz)]
        for i in range(self.sz):
            self.const_dict[i]['pass'] = 0
            self.const_dict[i]['fail'] = 0
        self.program_dict = [{} for _ in range(self.sz)]
        SynFunExpr = []
        for expr in expr:
            if len(expr)==0:
                continue
            elif expr[0]=='synth-fun':
                SynFunExpr=expr
        self.FuncDefine = ['define-fun'] + SynFunExpr[1:4]

    def check(self, tree):
        FuncDefineStr = translator.toString(self.FuncDefine,
                                            ForceBracket=True)
        CurrStr = translator.toString(tree)
        Str = FuncDefineStr[:-1] + ' ' + CurrStr + FuncDefineStr[-1]
        print('Curr ' + Str)
        examples, sz = self.checker.check(Str)
        rewards = 1.0
        if len(examples) == 0:
            print('Found')
            print(Str)
            quit()
        for key in examples.keys():
            constraint_id, example = key, examples[key]
            if Str in self.program_dict[constraint_id].keys():
                self.program_dict[constraint_id][Str] = self.program_dict[constraint_id][Str] * .9 + 1.0
            else:
                self.program_dict[constraint_id][Str] = 1

            if example in self.ce_dict[constraint_id].keys():
                self.ce_dict[constraint_id][example] = self.ce_dict[constraint_id][example] * .7 + 1.0
            else:
                self.ce_dict[constraint_id][example] = 1

        for constraint_id in range(sz):
            if constraint_id not in examples.keys():
                self.const_dict[constraint_id]['pass'] += 1
            else:
                self.const_dict[constraint_id]['fail'] += 1
            if constraint_id not in examples.keys():
                # pass
                rewards += len(self.ce_dict[constraint_id].keys()) / float(self.const_dict[constraint_id]['pass'])
            else:
                rewards -= len(self.ce_dict[constraint_id].keys()) * float(self.const_dict[constraint_id]['fail'])
        return rewards
