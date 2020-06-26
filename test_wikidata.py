
import time
import random
import kgpl

if __name__ == "__main__":
    store = kgpl.KNPSStore(None)
    tempList = []
    for i in range(10):
        tempint = random.randint(1, 10000)
        tempList.append(tempint)

    for i in tempList:
        print("----------")
        temp = time.time()
        a = kgpl.Wiki_Dict_Transformer("Q" + str(i))
        print("Wiki_Dict_Transform: ")
        print(str(time.time() - temp))
        temp = time.time()
        b = kgpl.KGPLDict(a)
        print("To KGPLDict: ")
        print(str(time.time() - temp))
        temp = time.time()
        store.StoreValues([b])
        print("Store: ")
        print(str(time.time() - temp))
        temp = time.time()
        store.PushValues()
        print("Push: ")
        print(str(time.time() - temp))
        temp = time.time()