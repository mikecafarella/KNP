from func_storage import *

class list_only_two_int_float:
    def __init__(self):
        self.__verystrict__ = True
    def compare_type(self, other):
        if type(other) is list:
            if len(other) != 2:
                return False
            if type(other[0]) is not int:
                return False
            if type(other[1]) is not float:
                return False
            return True
        else:
            return False


def strict_func(a: list_only_two_int_float):
    print("$$$$$$$$$$$")
    print("strict_func invoked, parameter: " + str(a) )
    print("$$$$$$$$$$$")


def test_func1():
    print("$$$$$$$$$$$")
    print("test_func1 invoked")
    print("$$$$$$$$$$$")


def myfunc(a: int, b: int):
    print("$$$$$$$$$$$")
    print("myfunc invoked, parameter: " + str(a) + " " + str(b))
    print("$$$$$$$$$$$")

# int or str
def union_test(a):
    print("$$$$$$$$$$$")
    print("union_test invoked, parameter: " + str(a))
    print("$$$$$$$$$$$")

def test1():
    print_table()
    a = FunctionWithSignature(myfunc, [int, int])
    b = FunctionWithSignature(test_func1, [])

    customized_type_object = list_only_two_int_float()
    c = FunctionWithSignature(strict_func, [customized_type_object,])


    store_func_table()
    print_table()


if __name__ == "__main__":
    test1()