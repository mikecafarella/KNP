import knps

def test_func1():
    print("test_func1")

def test1():
    print("hello")
    a = knps.FunctionWithSignature(test_func1, [])
    print(a)

def test2():
    print(type(test_func1))

def info(country: str, population: str, percentage: float):
    result = "The population of " + country + " is " + population + ", taking " + str(percentage) + " percent of EU."
    return result


# def double_dict():
#     val = 

if __name__ =="__main__":
    # test1()
    # test2()

