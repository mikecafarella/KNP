infile = open('/data/wikidata/latest-all.json', "rt")
outfile = open('small.json', 'wt')

nn = infile.read(2)
outfile.write(nn)

for i in range(0, 10):
    nn = infile.readline()
    outfile.write(nn)

nn.write(']\n')

infile.close()
outfile.close()