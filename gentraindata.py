
import os
import gzip
import pickle

#(self.list_synths, self.list_constraints, expr, i, k, j)

import csv


def main():
    files = os.listdir('/home/wenjie/sygusdata')
    foutput = open('stat.csv', 'w', newline='')
    writer = csv.writer(foutput)
    for f in files:
        fin = gzip.open(os.path.join('/home/wenjie/sygusdata', f), 'rb')
        list_synths, list_constraints, expr, pos, idxnon, idxrule = pickle.load(fin)

        num_ter = len(list_synths)
        max_rules = max([len(r) for n, r in list_synths])
        max_rule_len = max([max(len(x) for x in r) for n, r in list_synths])
        num_con = len(list_constraints)
        max_con_len = max([len(x) for x in list_constraints])
        expr_len = len(expr)
        writer.writerow((f, num_ter, max_rules, max_rule_len, num_con, max_con_len, expr_len))
    foutput.close()


if __name__ == "__main__":
    main()