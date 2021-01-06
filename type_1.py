from func_storage import *

def func_1(a):
    print(type(a))

    print(a)

def test1():
    a = FunctionWithSignature(func_1, [list])
    a.invoke([])

if __name__ == "__main__":
    test1()
