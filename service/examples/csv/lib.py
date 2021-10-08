import requests
import json
import base64

API_URL = ""

def get_user_id(email, name):
    url = "http://localhost:5000/users"
    data = {
        'email': email,
        'name': name
    }
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))

    user_data = response.json()
    user_id = user_data['id']

    return user_id


def create_data_object(name, ownerid, description, comment, data=None, datafile=None, predecessors=[]):
    url = "http://localhost:5000/dobjs"
    metadata = {
        'name': name,
        'owner_id': ownerid,
        'description': description,
        'comment': comment,
        'datatype': '/datatypes/csv',
        'data': data,
        'mimetype': 'text/csv',
        'predecessors': predecessors,
    }

    files = {}
    if datafile:
        files = {'datafile': open(datafile,'rb')}

    files['metadata'] = json.dumps(metadata)

    response = requests.post(url, files=files)
    obj_data = response.json()

    return obj_data

def update_data_object(objectid, ownerid, comment, data=None, datafile=None, predecessors=[]):
    url = "http://localhost:5000/versions"
    metadata = {
            'owner_id': ownerid,
            'dobj_id': objectid,
            'comment': comment,
            'datatype': '/datatypes/csv',
            'mimetype': 'text/csv',
            'data': data,
            'predecessors': predecessors,
        }

    files = {}
    if datafile:
        files = {'datafile': open(datafile,'rb')}

    files['metadata'] = json.dumps(metadata)

    response = requests.post(url, files=files)
    obj_data = response.json()

    return obj_data

def get_data_object(objectid):
    url = "http://localhost:5000/dobjs/{}".format(objectid)
    response = requests.get(url)
    obj_data = response.json()
    version_id = obj_data['versions'][0]['id']

    url = "http://localhost:5000/version/{}".format(version_id)
    response = requests.get(url)
    version_data = response.json()

    jsondata = json.loads(base64.b64decode(version_data['contents']['contents']))

    return {'jsondata': jsondata, 'version_id': version_id}
