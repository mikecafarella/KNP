import typing


def func2(lol: typing.Tuple[int]):
    print(lol)

def func1(lol: typing.List[int]):
    print(lol)

def test2():
    func2(("gdp", 1))

def test1():
    func2((1, 2))


if __name__ == "__main__":
    test1()
    test2()
