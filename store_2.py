from func_storage import *



def test1(a, b):
    print("$$$$$$$$$$$")
    print("test1 invoked, parameter: ")
    print(a)
    print(b)
    print("$$$$$$$$$$$")


def test2():
    print(func_table.table)
    a = FunctionWithSignature("test1", [int, int], test1)
    a.invoke(1,2)
    a.store()
    print(func_table.table)
    store_func_table()

def test3():
    print_table()
    print(func_table)
    # print(func_table.table)
    load_func_table()
    # print(func_table.table)
    print(func_table)
    print_table()

def test4():
    print_table()
    a = load_func_table()
    print_table()
    a.table["test1"].invoke(1,2)

def test5():
    a = load_func_table()
    print_table()
    # for k,v in a.table.items():
        # v.invoke()
    # a.table["test_func1"].invoke()
    a.table["myfunc"].invoke(1, 2)
    a.table["myfunc"].invoke(1, "str")


def test6():
	with open("func_lib/func_table_store", 'rb') as in_table:
		func_table = pickle.load(in_table)
		print(func_table.table)

def test8():
    with open("func_lib/func_table_store", 'rb') as in_table:
        load_back = pickle.load(in_table)
        print("in test8")
        print(load_back.table)

if __name__ == "__main__":
    # test1(1,2)
    # test2()
    # test3()
    # test4()
    test5()
    # test6()
    # test8()