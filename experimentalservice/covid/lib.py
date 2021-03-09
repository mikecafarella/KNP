import requests
import json

API_URL = ""

def get_user_id(email, name):
    url = "http://localhost:3000/api/user"
    data = {
        'email': email,
        'name': name,
    }
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))

    user_data = response.json()
    user_id = user_data['id']

    return user_id


def create_data_object(name, ownerid, description, jsondata, comment, predecessors=[]):
    url = "http://localhost:3000/api/createdataobj"
    data = {
        'metadata': {
            'name': name,
            'ownerid': ownerid,
            'description': description,
            'comment': comment,
            'datatype': '/datatypes/json',
            'jsondata': jsondata,
            'predecessors': predecessors,
        }
    }
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))

    obj_data = response.json()
    return obj_data

def update_data_object(objectid, ownerid, jsondata, comment, predecessors=[]):
    url = "http://localhost:3000/api/updatedataobj"
    data = {
        'metadata': {
            'ownerid': ownerid,
            'dobjid': objectid,
            'comment': comment,
            'datatype': '/datatypes/json',
            'jsondata': jsondata,
            'predecessors': predecessors,
        }
    }
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))

    obj_data = response.json()
    return obj_data

def get_data_object(objectid):
    url = "http://localhost:3000/api/dobj/X{}".format(objectid)
    response = requests.get(url)
    obj_data = response.json()
    return json.loads(obj_data['dobj']['JsonData'][0]['jsondata'])
