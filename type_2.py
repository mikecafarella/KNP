import typing
import dill
# # # print(isinstance(int, type))
# # print (typing.Union.__class__)
# # # print(issubclass(typing.Union, typing.Generic))
# # print(type(typing.Union[int, float]))
# a  = typing.Union[int, float]
# # # a  = typing.List[float]

# if a.__origin__ is typing.Union:
#     print("lol")

# # if type(a) is typing.GenericMeta:
# #     print("lol")
# # else:
# #     print(type(a))

# # a = 2
# # print(i)

# a = "dummy"
# print(a is "dummy")
a = typing.Union[int, str]
with open("dill_typing", 'wb') as dt:
    dill.dump(a, dt) 

