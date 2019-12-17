
import gzip
import pickle
import os

data_count = 0


def write(data):
    global data_count
    os.makedirs('data/', exist_ok=True)
    foutput = gzip.open(f"data/{data_count:04d}.tgz", "wb")
    pickle.dumps(data)
    foutput.close()
    data_count += 1
