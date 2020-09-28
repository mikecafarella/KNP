import os
import pickle

class id_gen_val:

    # self.current

    def __init__(self):
        if os.path.exists("log_val_id"):
            infile = open("log_val_id", "rb")
            self.current = pickle.load(infile)
            infile.close()
        else:
            self.current = 0

    def next(self):
        copy = self.current
        self.current += 1
        outfile = open("log_val_id", "wb")
        pickle.dump(self.current, outfile)
        outfile.close()
        return copy


class id_gen_var:

    # self.current

    def __init__(self):
        if os.path.exists("log_var_id"):
            infile = open("log_var_id", "rb")
            self.current = pickle.load(infile)
            infile.close()
        else:
            self.current = 0

    def next(self):
        copy = self.current
        self.current += 1
        outfile = open("log_var_id", "wb")
        pickle.dump(self.current, outfile)
        outfile.close()
        return copy

