import csv
import gzip
import os
import pickle

import h5py

import numpy as np
import random


def pad_to_len(m, l):
    if len(m) > l:
        return m[l:]
    else:
        m = np.array(m, copy=False)
        result = np.empty(shape=((l,) + m.shape[1:]), dtype=m.dtype)
        result[: len(m)] = m
        result[len(m) :] = 0
        return result

def gendata(list_synths, list_constraints, expr, pos, idxnon, idxrule=None):
    list_synths_np = []
    for non, rules in list_synths:
        rules = np.stack([pad_to_len(rule, 10) for rule in rules], axis=0)
        rules = pad_to_len(rules, 50)
        list_synths_np.append(rules)
    list_synths_np = np.stack(list_synths_np, axis=0)
    list_synths_np = pad_to_len(list_synths_np, 5)
    list_synths_np = np.reshape(list_synths_np, [-1])

    list_constraints_np = [pad_to_len(con, 200) for con in list_constraints]
    list_constraints_np = np.stack(list_constraints_np)
    list_constraints_np = pad_to_len(list_constraints_np, 20)
    list_constraints_np = np.reshape(list_constraints_np, [-1])

    expr_np = pad_to_len(expr, 1000)

    input_np = np.concatenate(
        [list_synths_np, list_constraints_np, expr_np], axis=0
    )

    if idxrule:
        return input_np, np.array(idxnon, dtype=np.int32), np.array(pos, dtype=np.int32), np.array(idxrule, dtype=np.int32)
    else:
        return input_np, np.array(idxnon, dtype=np.int32), np.array(pos, dtype=np.int32)

def main():
    files = os.listdir("/home/wenjie/sygusdata")
    random.shuffle(files)

    outputdata = h5py.File('train.h5')
    output_seq = outputdata.create_dataset('seq', shape=[len(files), 7500], dtype=np.int32)
    output_idxnon = outputdata.create_dataset('idxnon', shape=[len(files)], dtype=np.int32)
    output_pos = outputdata.create_dataset('pos', shape=[len(files)], dtype=np.int32)
    output_idxrule = outputdata.create_dataset('idxrule', shape=[len(files)], dtype=np.int32)

    foutput = open("stat.csv", "w", newline="")
    writer = csv.writer(foutput)
    for i, f in enumerate(files):
        fin = gzip.open(os.path.join("/home/wenjie/sygusdata", f), "rb")
        list_synths, list_constraints, expr, pos, idxnon, idxrule = pickle.load(fin)

        list_synths_np = []
        for non, rules in list_synths:
            rules = np.stack([pad_to_len(rule, 10) for rule in rules], axis=0)
            rules = pad_to_len(rules, 50)
            list_synths_np.append(rules)
        list_synths_np = np.stack(list_synths_np, axis=0)
        list_synths_np = pad_to_len(list_synths_np, 5)
        list_synths_np = np.reshape(list_synths_np, [-1])

        list_constraints_np = [pad_to_len(con, 200) for con in list_constraints]
        list_constraints_np = np.stack(list_constraints_np)
        list_constraints_np = pad_to_len(list_constraints_np, 20)
        list_constraints_np = np.reshape(list_constraints_np, [-1])

        expr_np = pad_to_len(expr, 1000)

        input_np = np.concatenate(
            [list_synths_np, list_constraints_np, expr_np], axis=0
        )

        output_seq[i,:] = input_np
        output_idxnon[i] = np.array(idxnon, dtype=np.int32)
        output_pos[i] = np.array(pos, dtype=np.int32)
        output_idxrule[i] = np.array(idxrule, dtype=np.int32)

        # [5, 50, 10] idxnon*500 + [0,49]*10
        # 6500+pos

        num_ter = len(list_synths)
        max_rules = max([len(r) for n, r in list_synths])
        max_rule_len = max([max(len(x) for x in r) for n, r in list_synths])
        num_con = len(list_constraints)
        max_con_len = max([len(x) for x in list_constraints])
        expr_len = len(expr)
        writer.writerow(
            (f, num_ter, max_rules, max_rule_len, num_con, max_con_len, expr_len)
        )
    foutput.close()


if __name__ == "__main__":
    main()
