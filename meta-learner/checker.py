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
            const = []
            for idx, constraint in enumerate(Constraints):
                self.solver.push()
                spec_smt2 = [funcDefStr]
                spec_smt2.append('(assert %s)' % (toString(constraint[1:])))
                spec_smt2 = '\n'.join(spec_smt2)
                # print spec_smt2
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
                    const.append((idx, model))
            return const

    checker = Checker(VarTable, synFunction, Constraints)
    return checker


class Checker:
    def __init__(self, expr):
        self.ce_dict = [{} for _ in range(10)]
        self.appear = {}
        self.pc = .7
        self.pm = .1
        self.n = 20
        self.checker = ReadQuery(expr)
        SynFunExpr = []
        for expr in expr:
            if len(expr)==0:
                continue
            elif expr[0]=='synth-fun':
                SynFunExpr=expr
        self.FuncDefine = ['define-fun']+SynFunExpr[1:4] #copy function signature

    def check(self, tree, step):
        FuncDefineStr = translator.toString(self.FuncDefine,
                                            ForceBracket=True)  # use Force Bracket = True on function definition. MAGIC CODE. DO NOT MODIFY THE ARGUMENT ForceBracket = True.
        CurrStr = translator.toString(tree)
        Str = FuncDefineStr[:-1] + ' ' + CurrStr + FuncDefineStr[-1]  # insert Program just before the last bracket ')'
        examples = self.checker.check(Str)
        rewards = 0.0
        print('Current: ' + Str)
        if len(examples) == 0:
            print('Found')
            print(Str)
        for item in examples:
            constraint_id, example = item
            if example in self.ce_dict[constraint_id].keys():
                self.ce_dict[constraint_id][example] += 1
            else:
                self.ce_dict[constraint_id][example] = 1
                self.appear[example] = step

        for constraint_id in range(10):
            diction = self.ce_dict[constraint_id]
            for key in diction.keys():
                if (constraint_id, key) not in examples:
                    rewards += diction[key] / float(step - self.appear[key] + 1)
        return rewards
