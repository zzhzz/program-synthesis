

class Checker:
    def __init__(self, solver):
        self.ce_dict = [set() for _ in range(10)]
        self.appear = {}
        self.pc = .7
        self.pm = .1
        self.n = 20
        self.solver = solver

    def check(self, tree, step):
        examples = self.solver.check(tree)
        rewards = 0.0
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







        pass