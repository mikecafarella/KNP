from elasticsearch import Elasticsearch


def store_record(index_name, record):
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    try:
        outcome = _es.index(
            index=index_name, body=record)
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))

re = {'url': 'http://localhost:3000/dobj/X19',
      'owner': 'owner',
      'comment': 'balabala',
      'pytype': '/datatypes/json}'}

store_record('kgpl', re)
