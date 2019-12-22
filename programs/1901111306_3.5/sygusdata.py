import gzip
import pickle
import os

data_count = 0

DATA_FOLDER = "/home/wenjie/sygusdata"


def write(data):
    global data_count
    os.makedirs(DATA_FOLDER, exist_ok=True)
    foutput = gzip.open(os.path.join(DATA_FOLDER, f"{data_count:04d}.tgz"), "wb")
    pickle.dump(data, foutput)
    foutput.close()
    data_count += 1
