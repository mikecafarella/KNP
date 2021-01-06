from func_storage import *

def test1():
    a = load_func_table()
    print_table()

def test2():
    a = load_func_table()
    print_table()
    a.table["myfunc"].invoke(1, 2)
    # a.table["myfunc"].invoke(1, "str")
    a.table["strict_func"].invoke([1, 1.2])
    # a.table["strict_func"].invoke([1, 1]) # incorrect

def test3():
    load_func_table()
    print_table()

    applyTableFunction("myfunc", 1, 2)
    # applyTableFunction("myfunc", 1, "str")

    applyTableFunction("strict_func", 1, 2) # incorrect
    applyTableFunction("strict_func", [1, 2.0])


if __name__ == "__main__":
    # test1()
    # test2()
    test3()