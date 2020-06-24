import time
import bz2
import threading
import json


chunk_size = 300*1000000
List0 = []
List1 = []
dict0 = {}
dict1 = {}
dict2 = {}
label_desc_dict = {}



def read_into_list0():
    global List0
    long_string = infile.read(chunk_size)
    if long_string[-1] == '\n':
        List0 = long_string.splitlines()
    else:
        List0 = long_string.splitlines()
        # make the last line complete and drop the new line character
        List0[-1] = (List0[-1] + infile.readline())[:-1]
    #print(len(List0))

def read_into_list1():
    global List1
    long_string = infile.read(chunk_size)
    if long_string[-1] == '\n':
        List1 = long_string.splitlines()
    else:
        List1 = long_string.splitlines()
        # make the last line complete and drop the new line character
        List1[-1] = (List1[-1] + infile.readline())[:-1]
    #print(len(List1))
def parse_into_dict_first_half(list_k):
    global label_desc_dict
    dict_k={}
    sz = len(list_k)
    for x in range(0, sz):
        #t1=time.time()
        obj = json.loads(list_k[x][:-1])
        #print(obj.keys())
        #t2=time.time()
        #print("load:{}".format(t2-t1))
        #t1=time.time()
        id = obj["id"]
        #print(id)
        dict_k[id]=[]
        dict_k[id].append(obj["labels"].get("en", {}).get("value"))
        dict_k[id].append(obj["descriptions"].get("en", {}).get("value"))
        #t2=time.time()
        #print("construct:{}".format(t2-t1))
        #print(dict_k)
    #t1=time.time()
    label_desc_dict.update(dict_k)
    #t2=time.time()
    #print("update:{}".format(t2-t1))

def parse_into_dict_second_half(list_k):
    global label_desc_dict
    dict_k={}
    sz = len(list_k)
    for x in range(sz // 2, sz):
        obj = json.loads(list_k[x][:-1])
        id = obj["id"]
        #print(id)
        dict_k[id]=[]
        dict_k[id].append(obj["labels"].get("en", {}).get("value"))
        dict_k[id].append(obj["descriptions"].get("en", {}).get("value"))
    label_desc_dict.update(dict_k)

def parse_into_dict_third_half(dict_k, list_k):
    dict_k.clear()
    sz = len(list_k)
    for x in range(sz // 3*2, sz):
        obj = json.loads(list_k[x][:-1])
        id = obj["id"]
        #print(id)
        dict_k[id]=[]
        dict_k[id].append(obj["labels"].get("en", {}).get("value"))
        dict_k[id].append(obj["descriptions"].get("en", {}).get("value"))


infile = open('/data/wikidata/latest-all.json', "rt")
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

# label_desc_dict = {}
# if r is even, then list0 is used to parse and loads into list1
# if r is odd, then list1 is used to parse and loads into list0
for r in range(0, 3300):
    if r % 2 == 0:
        time1 = time.time()
        t0 = threading.Thread(target=read_into_list1)
        # lt1=List0[:]
        # lt2=List0[:]
        t1 = threading.Thread(target=parse_into_dict_first_half, args=(List0,))
        #t2 = threading.Thread(target=parse_into_dict_second_half, args=(List0,))
        # t3 = threading.Thread(target=parse_into_dict_third_half, args=(dict2, List0))
        t0.start()
        t1.start()
        #t2.start()
        # t3.start()
        t0.join()
        t1.join()
        #t2.join()
        # t3.join()
        #print(dict0)
        #print(dict1)
        #print(len(List1))
        #label_desc_dict.update(dict0)
        #label_desc_dict.update(dict1)
        print(r, time.time() - time1)
    else:
        time1 = time.time()
        # lt1=List1[:]
        # lt2=List1[:]
        t0 = threading.Thread(target=read_into_list0)
        t1 = threading.Thread(target=parse_into_dict_first_half, args=(List1,))
        #t2 = threading.Thread(target=parse_into_dict_second_half, args=(List1,))
        # t3 = threading.Thread(target=parse_into_dict_second_half, args=(dict2, List1))
        t0.start()
        t1.start()
        #t2.start()
        # t3.start()
        t0.join()
        t1.join()
        #t2.join()
        # t3.join()
        #print(len(List0))
        #label_desc_dict.update(dict0)
        #label_desc_dict.update(dict1)
        print(r, time.time() - time1)

# dump json
print("begin dump *********************")
time1 = time.time()
#print(label_desc_dict)
outfile = open("tongtong.txt", "wt")
json.dump(label_desc_dict, outfile)
outfile.close()
print("finish dump", time.time() - time1)


    

