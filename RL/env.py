import json
import translator

class Enviroment:
    def __init__(self, expr, signature):
        self.checker = translator.ReadQuery(expr)
        self.signatrue = signature
        self.result = ''
        self.adv_st = {}
        self.program_st = {}

    def rewards(self, program, dep, epoch):
        FuncDefineStr = translator.toString(self.signatrue, ForceBracket=True)  # use Force Bracket = True on function definition. MAGIC CODE. DO NOT MODIFY THE ARGUMENT ForceBracket = True.
        CurrStr = translator.toString(program)
        Str = FuncDefineStr[:-1] + ' ' + CurrStr + FuncDefineStr[-1]  # insert Program just before the last bracket ')'
        print(Str)
        counterexample, counter = self.checker.check(Str)
        if len(counterexample) == 0:  # No counter-example
            print('Found!')
            self.result = Str
            quit()
            return 10
        else:
            r = 0
            example_str = Str
            if example_str in self.adv_st.keys():
                r += self.adv_st[example_str]
                self.adv_st[example_str] += 1
            else:
                r += 1
                self.adv_st[example_str] = 1
            r = counter - r/10.0
            return r
