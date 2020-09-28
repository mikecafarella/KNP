import kgpl
import requests
import json
from collections import defaultdict
from datetime import datetime, timedelta


def example1():
    my_test_string = "First Value."
    myval = kgpl.value(my_test_string)
    kgpl.variable(myval.vid)

    my_test_string2 = "Second Value."
    myval2 = kgpl.value(my_test_string2)
    kgpl.variable(myval2.vid)


def example2():
    for i in range(10):
        test_string = "value" + str(i)
        myval = kgpl.value(test_string)
        kgpl.variable(myval.vid)



if __name__ == "__main__":
    example1()
    example2()
