import knps


def func_1(a, b):
    print("func_1 invoked with:", end=' ')
    print(a, end=' ')
    print(b)


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
    print("strict_func invoked, parameter: " + str(a))
    print("$$$$$$$$$$$")


def strict_func_two_para(a: list_only_two_int_float, b: int):
    print("$$$$$$$$$$$")
    print("strict_func_two_para invoked, first parameter: " + str(a) + "second parameter: "+str(b))
    print("$$$$$$$$$$$")


def test1():
    fh = knps.FunctionWithSignature(func_1, [int, str])
    knps.publish_new(fh, "test func 1", "alice")

def test2():
    customized_type_object = list_only_two_int_float()
    c = knps.FunctionWithSignature(strict_func, [customized_type_object, ]) # first test only one
    knps.publish_new(c, "strict func 1", "strict")

def test3():
    customized_type_object = list_only_two_int_float()
    c = knps.FunctionWithSignature(strict_func_two_para, [customized_type_object, int]) # test multiple
    knps.publish_new(c, "strict func with 2 paras", "two_para")


# test1()
# test2()
test3()
