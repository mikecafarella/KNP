import requests
import json
from elasticsearch import Elasticsearch
import datetime

API_URL = ""


def store_record(index_name, record):
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    try:
        outcome = _es.index(
            index=index_name, body=record)
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))


def get_user_id(email, name):
    url = "http://localhost:3000/api/user"
    data = {
        'email': email,
        'name': name
    }
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))

    user_data = response.json()
    user_id = user_data['id']

    return user_id


def create_data_object(name, ownerid, description, comment, ownername='Alice', jsondata=None, image_file=None, pdf_file=None, predecessors=[]):
    url = "http://localhost:3000/api/createdataobj"
    metadata = {
        'name': name,
        'ownerid': ownerid,
        'description': description,
        'comment': comment,
        'datatype': '/datatypes/json',
        'jsondata': jsondata,
        'predecessors': predecessors,
    }
    re = {'url': 'http://localhost:3000/dobj/X19',
          'owner': ownername,
          'comment': comment,
          'pytype': '/datatypes/json}',
          'timestamp': 0
          }

    files = {}
    if image_file:
        metadata['datatype'] = '/datatypes/img'
        re['pytype'] = '/datatypes/img'
        files = {'imgpath': (image_file, open(image_file, 'rb'), 'image/jpg')}
    elif pdf_file:
        metadata['datatype'] = '/datatypes/pdf'
        re['pytype'] = '/datatypes/pdf'
        files = {'pdfpath': (pdf_file, open(
            pdf_file, 'rb'), 'application/pdf')}

    files['metadata'] = (None, json.dumps(metadata), 'application/json')
    


    response = requests.post(url, files=files)
    obj_data = response.json()
    data_obj_id = obj_data['data']['dobjid']
    # print(obj_data["timestamp"])
    # print(type(obj_data["timestamp"]))
    date_time_zjy_obj = datetime.datetime.strptime(obj_data["timestamp"], '%Y-%m-%dT%H:%M:%S.%fZ')
    re['timestamp'] = date_time_zjy_obj.replace(microsecond=0).isoformat()

    re['url'] = 'http://localhost:3000/dobj/X'+str(data_obj_id)
    # Elastic
    store_record('kgpl', re)
    
    return obj_data


def update_data_object(objectid, ownerid, comment, jsondata=None, image_file=None, pdf_file=None, predecessors=[]):
    url = "http://localhost:3000/api/updatedataobj"
    metadata = {
        'ownerid': ownerid,
        'dobjid': objectid,
        'comment': comment,
        'datatype': '/datatypes/json',
        'jsondata': jsondata,
        'predecessors': predecessors,
    }

    files = {}
    if image_file:
        metadata['datatype'] = '/datatypes/img'
        files = {'imgpath': (image_file, open(image_file, 'rb'), 'image/jpg')}
    elif pdf_file:
        metadata['datatype'] = '/datatypes/pdf'
        files = {'pdfpath': (pdf_file, open(
            pdf_file, 'rb'), 'application/pdf')}

    files['metadata'] = (None, json.dumps(metadata), 'application/json')

    response = requests.post(url, files=files)

    obj_data = response.json()

    
    return obj_data


def get_data_object(objectid):
    url = "http://localhost:3000/api/dobj/X{}".format(objectid)
    response = requests.get(url)
    obj_data = response.json()
    jsondata = json.loads(obj_data['dobj']['JsonData'][0]['jsondata'])
    version_id = obj_data['dobj']['id']
    return {'jsondata': jsondata, 'version_id': version_id}
