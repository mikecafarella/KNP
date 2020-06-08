import kgpl
from kgpl import KNPSStore

if __name__ == "__main__":
    store = KNPSStore('http://lasagna.eecs.umich.edu:8080')
    a = kgpl.getValue("22a9d095-a520-4b69-9ac0-b76a26b5ed87")
    print(a.__repr__())

    b = kgpl.KGPLInt(44)
    store.StoreValues([b])
    store.PushValues()