Wikidata embedding
==================

Gensim model: 
wikidata-20170613-truthy-BETA-cbow-size=100-window=1-min_count=20

Download of Wikidata from::

    https://dumps.wikimedia.org/wikidatawiki/entities/

Trigram construction::

    from bz2 import BZ2File
    import re

    dump_filename = 'wikidata-20170613-truthy-BETA.nt.bz2'
    trigram_filename = 'wikidata-20170613-truthy-BETA.trigrams'

    pattern = re.compile(
        (r'^<http://www.wikidata.org/entity/(Q\d+)> '
         r'<http://www.wikidata.org/prop/direct/(P\d+)> '
         r'<http://www.wikidata.org/entity/(Q\d+)>'),
         flags=re.UNICODE)

    with open(trigram_filename, 'w') as f:
        for line in BZ2File(dump_filename):
            line = line.decode('utf-8')
            match = pattern.search(line)
            if match:
                f.write(" ".join(match.groups()) + '\n')


Construction of Gensim model::
		
    import logging
    from gensim.models import Word2Vec
    from gensim.models.word2vec import LineSentence

    logging.basicConfig(
        format='%(asctime)s : %(levelname)s : %(message)s',
        level=logging.INFO)

    sentences = LineSentence('wikidata-20170613-truthy-BETA.trigrams')

    filename = 'wikidata-20170613-truthy-BETA-cbow-size=100-window=1-min_count=20'
    w2v = Word2Vec(sentences, size=100, window=1, min_count=20, workers=10)
    w2v.save(filename)

