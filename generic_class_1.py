import typing
import pickle

from typing import Union, List, TypeVar 

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


# see if a is b
def checkType(a, b):
    # print(type(a))
    # print(a)
    # print(type(b))
    # print(b)
    if type(a) is b:
        return True
    try:
        if b.__origin__ is typing.Union: # have several choices
            for i in b.__args__:
                if type(a) is i:
                    return True
            return False
        elif b.__origin__ is typing.List: # list can only have one type
            if type(a) is list:
                for i in a:
                    if type(i) is not b.__args__[0]:
                        return False
                return True
            else:
                return False            
        elif b.__origin__ is typing.Tuple:
            if len(a) != len(b.__args__):
                return False
            if type(a) is tuple:
                for i, j in enumerate(a):
                    if type(j) is not b.__args__[i]:
                        return False
                return True
            else:
                return False
        elif b.__origin__ is typing.Dict: # all key value pairs should be the same
            if type(a) is dict:
                for k, v in a.items():
                    print("here 3")
                    if type(k) is not b.__args__[0] or type(v) is not b.__args__[1]:
                        return False
                return True
            else:
                return False
    except:
        pass
    try:
        if b.__verystrict__:
            temp_b = b()
            return temp_b.compare_type(a)
    except:
        pass
    return False
        
        
# print(checkType([1,2.0], list_only_two_int_float))
# print(checkType(1, typing.Union[float, str]))
# print(checkType(1, typing.Union[float, str, int]))
# print(checkType([1,2,3], typing.List[int]))
# print(checkType([1,"str",3], typing.List[int]))
# print(checkType((1,2,3), typing.Tuple[int]))
# print(checkType((1,2,3), typing.Tuple[int, int, int]))
# print(checkType((1,"ba",3), typing.Tuple[int, str, int]))
# print(checkType((1,2,3), typing.Tuple[int, str, int]))
# print(checkType({"str": 1}, typing.Dict[str, str]))
# print(checkType({"str": "val"}, typing.Dict[str, str]))




# a = list_of_int()
# print(type(a))

# def customizedCheck(actual_para, required_para):
#     # list_of_int = (1, 2, 3)
#     # paramList = [int, int, int]
#     # print(required_para)

#     typedParams = zip(actual_para, required_para)
#     # print(typedParams)
    
#     typeCheckResults = list(map(lambda x: checkType(x[0], x[1]), typedParams))
#     print(typeCheckResults)

# Note: The informal convention is to prefix all typevars with
# either 'T' or '_T' -- so 'TNum' or '_TNum'.
# TNum = TypeVar('TNum', List[int])


# # customizedCheck([[1,2,3],], [List[int], ])
# a = 42
# print(a.__origin__)
# a = List[int]
# print(a.__origin__)
# print(a.__args__)

# def quick_sort_before(arr: List[TNum]) -> List[TNum]:
#     return arr

# with open("test_pickle_TypeVar", 'wb') as out_file:
#     pickle.dump(TNum, out_file)

# with open("test_pickle_TypeVar", 'rb') as out_file:
#     a = pickle.load(out_file)
#     print(a)
#     print(type(a))



# foo = [1, 2, 3, 4]  # type: List[int]
# print(quick_sort_before(foo))

# bar = [1.0, 2.0, 3.0, 4.0]  # type: List[float]
# print(quick_sort_before(foo))

# # foo = [1, 2, 3, 4]  # type: List[int]
# # quick_sort_after(foo)

# # bar = [1.0, 2.0, 3.0, 4.0]  # type: List[float]
# # quick_sort_after(foo)
