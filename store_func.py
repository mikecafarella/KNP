import pickle


class funcpt:
    def __init__(self, func):
        self.fp = func


def test1():
    print("1")

func_table = {}

def try1():
    a = funcpt(test1)
    func_table["test"] = a
    print(func_table)
    b = pickle.dumps(func_table)
    with open("func_table", 'wb') as func_table_file:
        pickle.dump(func_table, func_table_file)
    print(b)
    c = pickle.loads(b)
    c["test"].fp()


def try2():
    with open ("func_table", 'rb') as func_table_file:
        a = pickle.load(func_table_file)
        a["test"].fp()

        
if __name__ == "__main__":
    # try1()
    try2()
