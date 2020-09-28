import json
import pandas

import ORM_modified as ORM
import kgpl
from kgpl import KGPLValue
from kgpl import KGPLVariable
pandas.set_option('display.max_rows', None)
pandas.set_option('display.max_columns', None)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, KGPLValue):
            return {"vid": obj.vid, "__kgplvalue__": True}
        elif isinstance(obj, KGPLVariable):
            return {"vid": obj.vid, "__kgplvariable__": True}
        elif isinstance(obj, ORM.Relation):
            return {
                "entity_id": obj.entity_id,
                "query_str": obj.query_str,
                "dic": obj.dic,
                "result_dic": obj.result_dic,
                "df": obj.df.to_json(),
                "count": obj.count,
                "verbose_count": obj.verbose_count,
                "time_property": obj.time_property,
                "time": obj.time,
                "limit": obj.limit,
                "focus": obj.focus,
                "trace": obj.trace.to_json(),
                "__relation__": True
            }
        return json.JSONEncoder.default(self, obj)


def hook(dct):
    if "__kgplvalue__" in dct:
        return load_val(dct["vid"])
    elif "__kgplvariable__" in dct:
        return load_var(dct["vid"])
    elif "__relation__" in dct:
        return ORM.Relation(dct["entity_id"], None, False, dct["limit"], False, False,
                            dct["time_property"], dct["time"], None, dct["query_str"], pandas.read_json(dct["trace"]), pandas.read_json(dct["df"]))

    return dct


def test2(relationship_generate):
    my_comment = "relationship generated by thrust 1"
    val = kgpl.value(relationship_generate.df, my_comment)
    print(val)


def test3(rel):
    a = json.dumps(rel, cls=MyEncoder)
    # print(a)
    my_dict = json.loads(a, object_hook=hook)
    print(my_dict)


def test6():
    my_comment = "relationship"
    val = kgpl.value(42, my_comment)


def test7():
    val = kgpl.load_val("http://127.0.0.1:5000/val/1")
    print(val)


def test5():
    url = "http://127.0.0.1:5000/val/0"
    val = kgpl.load_val(url)
    print(val)
    print(val.val)
    print(type(val.val))


def test1():
    r = ORM.createRelation("Q458")
    r.extend("P150", False, "Countries")
    r.changeFocus("Countries")
    r.extend("P2131", False, "GDP")
    r.extend("P36", False, "Capitals")
    # r.changeFocus("Capitals")
    # r.extend("P1082", False, "Population_of_capitals")
    r.query()
    return r


def test4(rel):
    my_comment = "relationship generated by thrust 1"
    val = kgpl.value(rel, my_comment)


def test8():
    r = ORM.createRelation("Q30")
    r.extend("P36", False, "Capital", rowVerbose=True, colVerbose=True)
    r.changeFocus("Capital")
    r.extend("P1082", False, "Population", rowVerbose=True, colVerbose=True)
    r.query()
    my_comment = "second test"
    user = "test2_user"
    kgpl.value(r,my_comment,user)

def test9():
    my_val = kgpl.load_val("http://lasagna.eecs.umich.edu:5000/val/0")

    print(my_val)
    print(type(my_val.val))
    re = my_val.val
    re.changeFocus("Capitals")
    re.extend("P1082", False, "Population_of_capitals")
    re.query()
    another_val = kgpl.value(re,"add Population_of_capitals")


if __name__ == "__main__":
    relation_from_thrust_one = test1()
    test4(relation_from_thrust_one)

    # Put them together
    # test8()
    test9()
