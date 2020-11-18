import knps


def test1():
    a = knps.create_value(42, "lalala")
    b = knps.variable("var1", a, "test", "alice")


def test2():
    a = knps.create_value(24, "lalala")
    d = knps.load_var("http://127.0.0.1:5000/var/haha")
    c = knps.set_var(d, a.vid, "haha")

def test3():
    c = knps.load_val("http://127.0.0.1:5000/val/0")
    # a = knps.variable("haha", c,"hahahahah","ben")
    c.create_label("hehe","hehe comment")


def test4():
    c = knps.create_value(18, "lalala")
    c.update_label("hehe", "new hehe")


def test5():
    a = knps.create_value(42, "42 is the answer")
    b = a.create_label("first_var", "a random var")
    c = knps.create_value(14, "Shakespeare")
    c.update_label("first_var","Shakespeare's sonnet")

if __name__=="__main__":
    # test1()
    # test2()
    # test3()
    # test4()
    test5()

