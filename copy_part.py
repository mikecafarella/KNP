infile = open('/data/wikidata/latest-all.json', "rt")
outfile = open('small.json', 'wt')

nn = infile.read(2)
outfile.write(nn)

for i in range(0, 120000):
    nn = infile.readline()
    outfile.write(nn)

nn = infile.readline()
outfile.write(nn[:-2])

outfile.write('\n]\n')

infile.close()
outfile.close()

