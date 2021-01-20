import knps


def test1():
    re = knps.get_label_content("alice")
    re.invoke(1, "2")


def test2():
    re = knps.get_label_content("strict")
    re.invoke([1, 2.0])

def test3():
    re = knps.get_label_content("two_para")
    re.invoke([1, 2.0], 10.0)


# test1()
# test2()
test3()
