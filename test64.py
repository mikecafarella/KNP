import kgpl
import KNPSStore

store = KNPSStore.KNPSStore('http://lasagna.eecs.umich.edu:4000')
a = kgpl.KGPLFloat(4578)
print(a.id)
store.StoreValues([a])
store.PushValues()