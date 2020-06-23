import time
import bz2
import threading
import json


chunk_size = 1000000
List0 = []
List1 = []
dict0 = {}
dict1 = {}


def read_into_list0():
    long_string = infile.read(chunk_size)
    if long_string[-1] == '\n':
        List0 = long_string.splitlines()
    else:
        List0 = long_string.splitlines()
        # make the last line complete and drop the new line character
        List0[-1] = (List0[-1] + infile.readline())[:-1]

def read_into_list1():
    long_string = infile.read(chunk_size)
    if long_string[-1] == '\n':
        List1 = long_string.splitlines()
    else:
        List1 = long_string.splitlines()
        # make the last line complete and drop the new line character
        List1[-1] = (List1[-1] + infile.readline())[:-1]

def parse_into_dict_first_half(dict_k, list_k):
    dict_k.clear()
    sz = len(list_k)
    for x in range(0, sz // 2):
        obj = json.loads(list_k[x][:-1])
        #print(obj.keys())
        id = obj["id"]
        print(id)
        dict_k[id]=[]
        dict_k[id].append(obj["labels"].get("en", {}).get("value"))
        dict_k[id].append(obj["descriptions"].get("en", {}).get("value"))
        print(dict_k)



def parse_into_dict_second_half(dict_k, list_k):
    dict_k.clear()
    sz = len(list_k)
    for x in range(sz // 2, sz):
        obj = json.loads(list_k[x][:-1])
        id = obj["id"]
        print(id)
        dict_k[id]=[]
        dict_k[id].append(obj["labels"].get("en", {}).get("value"))
        dict_k[id].append(obj["descriptions"].get("en", {}).get("value"))


infile = bz2.open('/data/wikidata/latest-all.json.bz2', "rt")
infile.read(2)

time1 = time.time()
# first read
long_string = infile.read(chunk_size)
if long_string[-1] == '\n':
    List0 = long_string.splitlines()
else:
    List0 = long_string.splitlines()
    # make the last line complete and drop the new line character
    List0[-1] = (List0[-1] + infile.readline())[:-1]
print("initial read", time.time() - time1)

label_desc_dict = {}
# if r is even, then list0 is used to parse and loads into list1
# if r is odd, then list1 is used to parse and loads into list0
for r in range(0, 3):
    if r % 2 == 0:
        time1 = time.time()
        t0 = threading.Thread(target=read_into_list1)
        t1 = threading.Thread(target=parse_into_dict_first_half, args=(dict0, List0))
        t2 = threading.Thread(target=parse_into_dict_second_half, args=(dict1, List0))
        t0.start()
        t1.start()
        t2.start()
        t0.join()
        t1.join()
        t2.join()
        print(dict0)
        print(dict1)
        label_desc_dict.update(dict0)
        label_desc_dict.update(dict1)
        print(r, time.time() - time1)
    else:
        time1 = time.time()
        t0 = threading.Thread(target=read_into_list0)
        t1 = threading.Thread(target=parse_into_dict_first_half, args=(dict0, List1))
        t2 = threading.Thread(target=parse_into_dict_second_half, args=(dict1, List1))
        t0.start()
        t1.start()
        t2.start()
        t0.join()
        t1.join()
        t2.join()
        label_desc_dict.update(dict0)
        label_desc_dict.update(dict1)
        print(r, time.time() - time1)

# dump json
print("begin dump *********************")
time1 = time.time()
print(label_desc_dict)
outfile = open("tongtong.txt", "wt")
json.dump(label_desc_dict, outfile)
outfile.close()
print("finish dump", time.time() - time1)


    

