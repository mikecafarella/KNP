import pickle


class list_only_two_int_float:
    __crazyclass__ = True

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


mylist = [int, list_only_two_int_float]

print(mylist[1].__crazyclass__)
