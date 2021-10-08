# https://stackoverflow.com/questions/40000495/how-to-encode-bytes-in-json-json-dumps-throwing-a-typeerror
import knps
import json
import dill
import pickle
import marshal
import base64
import types


def func_1(a, b=[], c="a"):
    print(a)
    print(b)
    print(c)
    print("func 1 invoked")


def test1():
    # func_1(1,c='b')
    print(type(func_1))
    print(isinstance(func_1, type(func_1)))
    print(func_1.__class__)
    print(type(func_1) is function)


def test2():
    f = knps.File("predict_1.png")
    b = knps.KGPLValue(f, "file test")
    print(b.val)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if (isinstance(obj, knps.FunctionWithSignature)):
            type_list = []
            for t in obj.typeSignature:
                encoded_obj = base64.b64encode(dill.dumps(t))
                type_list.append(encoded_obj.decode('ascii'))
            encoded_code = base64.b64encode(marshal.dumps(obj.fn.__code__))
            encoded_defaults = base64.b64encode(
                pickle.dumps(obj.fn.__defaults__))
            encoded_closure = base64.b64encode(
                pickle.dumps(obj.fn.__closure__))
            return {
                "types": type_list,
                "customized": customized_list,
                "__funcwithsig__": True,
                "code": encoded_code.decode('ascii'),
                "defaults": encoded_defaults.decode('ascii'),
                "closure": encoded_closure.decode('ascii')
            }
        return json.JSONEncoder.default(self, obj)


def hook(dct):
    if "__funcwithsig__" in dct:
        type_list = []
        for t in dct["types"]:
            decode_type = base64.b64decode(t)
            type_list.append(dill.loads(decode_type))

        decoded_code = base64.b64decode(dct["code"])
        decoded_defaults = base64.b64decode(dct["defaults"])
        decoded_closure = base64.b64decode(dct["closure"])

        marshaled_func = marshal.loads(decoded_code)
        pickled_arguments = pickle.loads(decoded_defaults)
        pickled_closure = pickle.loads(decoded_closure)

        fn = types.FunctionType(marshaled_func, globals(),
                                "funcname", pickled_arguments, pickled_closure)

        return knps.FunctionWithSignature(fn, type_list)
    return dct


def test3():
    func = knps.FunctionWithSignature(func_1, [int])
    # print(type(func))
    # print(";;;;;;;;")
    a = json.dumps(func, cls=MyEncoder)
    print(a)
    tmp_val = json.loads(a, object_hook=hook)
    tmp_val.fn(1)


if __name__ == "__main__":
    # test1()
    # test2()
    test3()
