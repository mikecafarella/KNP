import typing


def func3(lol: str):
    print(lol)


def func2(lol: typing.Tuple[int, int]):
    print(lol)


def func1(lol: typing.List[int]):
    print(lol)


def test2():
    func2(("gdp", 1))
    func3(1)


def test1():
    func2((1, 2))

test2()
func2(("gdp", 1))
func1([1,2,3])
func1(["a",1,2])

