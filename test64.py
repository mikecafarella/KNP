import kgpl
from kgpl import KNPSStore

store = KNPSStore('http://lasagna.eecs.umich.edu:4000')
a = kgpl.getValue("22a9d095-a520-4b69-9ac0-b76a26b5ed87")
print(a.__repr__())

b = kgpl.KGPLInt(44)
store.StoreValues([b])
store.PushValues()
