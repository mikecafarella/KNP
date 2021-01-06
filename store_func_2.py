import pickle


class funcpt:
    def __init__(self, func):
        self.fp = func


def try2():
    with open ("func_table", 'rb') as func_table_file:
        a = pickle.load(func_table_file)
        # a["test"].fp()

        
if __name__ == "__main__":
    # try1()
    try2()
