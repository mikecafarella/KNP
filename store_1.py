from func_storage import *


# def test1(a: str, b: str):
#     print("$$$$$$$$$$$")
#     print("test1 invoked, parameter: " + str(a) +" "+ str(b))
#     print("$$$$$$$$$$$")


def test_func1():
    print("$$$$$$$$$$$")
    print("test3 invoked")
    print("$$$$$$$$$$$")


def test2():
    print_table()
    a = FunctionWithSignature(test1, [int, int])
    a.invoke(1, 2)
    # a.store()
    print("***********")
    store_func_table()
    print_table()


def test3():
    print(test1.__annotations__)


def test_func1():
    print("$$$$$$$$$$$")
    print("test_func1 invoked")
    print("$$$$$$$$$$$")


def test4():
    a = FunctionWithSignature(test_func1, [])
    a.invoke()
    store_func_table()
    print_table()


def test_func2(i: int):
    print("$$$$$$$$$$$")
    print("test_func1 invoked with " + str(i))
    print("$$$$$$$$$$$")


def test5():
    a = FunctionWithSignature(test_func2, [int, ])
    a.invoke(42)
    store_func_table()
    print_table()


def test_func3(a: int, b: int):
    print("test_func3 invoked with " + str(a)+" "+str(b))


def test6():
    a = FunctionWithSignature(test_func3, [int, int])
    store_func_table()
    print_table()


def test_func4(a: str, b: str):
    print("$$$$$$$$$$$")
    print("test1 invoked, parameter: " + str(a) + " " + str(b))
    print("$$$$$$$$$$$")


def myfunc(a: str, b: str):
    print("$$$$$$$$$$$")
    print("myfunc invoked, parameter: " + str(a) + " " + str(b))
    print("$$$$$$$$$$$")


def test7():
    print_table()
    a = FunctionWithSignature(myfunc, [int, int])
    # a.invoke(1, 2)
    b = FunctionWithSignature(test_func1, [])
    print("***********")
    store_func_table()
    print_table()
    # with open("func_lib/func_table_store", 'rb') as in_table:
    #     load_back = pickle.load(in_table)
    #     print("in test7")


if __name__ == "__main__":
    # test1(1,2)
    # test2()
    # test3()
    # test4()
    # test5()
    # test6()
    test7()
    # test8()
