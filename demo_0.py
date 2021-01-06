from func_storage import *
import typing


def test(a):
    print("test invoked with: " + str(a))


def test_two(a, b):
    print("test_two invoked with: " + str(a) + " " + str(b))

def d1():
    z = FunctionWithSignature(test_two, [int, int])
    z.invoke(1, 2)
    # z.invoke("a", 2)  # incorrect
    y = FunctionWithSignature(test, [int,])
    y.invoke(1)
    # y.invoke("str")

def d2():
    a = FunctionWithSignature(test, [typing.Union[float, str],])
    # a.invoke(1) # incorrect
    b = FunctionWithSignature(test, [typing.Union[float, str, int],])
    b.invoke(1)
    c = FunctionWithSignature(test,[typing.List[int]])
    c.invoke([1, 2, 3])
    # c.invoke([1,"str",3]) # incorrect
    d = FunctionWithSignature(test, [typing.Tuple[int]])
    # d.invoke((1,2,3)) # incorrect
    e = FunctionWithSignature(test, [typing.Tuple[int, int, int]])
    e.invoke((1, 2, 3))
    f = FunctionWithSignature(test, [typing.Tuple[int, str, int]])
    # f.invoke((1,2,3)) # incorrect
    g = FunctionWithSignature(test, [typing.Dict[str, str]])
    # g.invoke({"str": 1}) #incorrect
    g.invoke({"str": "val"})


class list_only_two_int_float:
    __verystrict__ = True

    def __init__(self):
        pass

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


def very_strict_func(a: list_only_two_int_float):
    print("$$$$$$$$$$$")
    print("myfunc invoked, parameter: " + str(a) )
    print("$$$$$$$$$$$")


def d3():
    user_defined_type = list_only_two_int_float()

    a = FunctionWithSignature(very_strict_func, [user_defined_type, ])
    a.invoke([1, 1.0])
    # a.invoke([1, 2]) # incorrect


if __name__ == "__main__":
    d1()
    d2()
    d3()
