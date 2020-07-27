import os
import pickle

class id_gen:

    # self.current

    def __init__(self):
        if os.path.exists("log"):
            infile = open("log", "rb")
            self.current = pickle.load(infile)
            infile.close()
        else:
            self.current = 0

    def next(self):
        copy = self.current
        self.current += 1
        outfile = open("log", "wb")
        pickle.dump(self.current, outfile)
        outfile.close()
        return copy


