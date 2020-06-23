import time
from itertools import islice
infile = open('/data/wikidata/latest-all.json.bz2', "rt")
time1 = time.time()
g = infile.readline(50000)
time2 = time.time()
print(time2-time1)
