from kgpl import KNPSStore
import kgpl
import os
import time

a = KNPSStore.KNPSStore("http://107.191.51.32:5000")

def store_a_new_value():
  print(a.valueList)
  b = kgpl.KGPLValue(3)
  print(str(b.id))
  print(b.__repr__())
  print("done")
  a.StoreValues([b])
  print(a.valueList)
  #a.GetValue("a")
  print("finished")
  return b

#new_value = store_a_new_value()
#print("start pushing")
#a.PushValues()
#print("finish pushing")
#a.GetValue(str(new_value.id))
#os.remove(os.path.join("val",str(new_value.id)))
#value = a.GetValue(str(new_value.id))
#print(value.__repr__())

val1 = kgpl.KGPLValue(2)
val2 = kgpl.KGPLValue(4)
print(val1.__repr__())
print(val2.__repr__())

a.StoreValues([val1, val2])
a.PushValues()
print("start register")
name = a.RegisterVariable(val1, time.time())
print("finish register")
print("get variable")
var = a.GetVariale(name)
print("finish get variable")
print(var.__repr__())

os.remove(os.path.join("var", name))
time.sleep(5)
a.SetVariable(name, val2, time.time())

print(var.__repr__())
