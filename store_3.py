
def checkType(a, b):
    if type(a) is b:
        return True
    else:
        return False


def test1():
    list_of_int = (1, 2, 3)
    paramList = [int, int, int]
    typedParams = zip(list_of_int, paramList)
    typeCheckResults = list(map(lambda x: checkType(x[0], x[1]), typedParams))
    print(typeCheckResults)


if __name__ == "__main__":
    test1()
