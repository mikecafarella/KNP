import ujson as json
import time

time1 = time.time()
infile = open("/data/wikidata/label_desc.txt", "rt")

obj = json.load(infile)
infile.close()
print(len(obj))
time2 = time.time()
print("load time", time2 - time1)
