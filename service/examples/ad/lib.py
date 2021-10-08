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


def create_data_object(name, ownerid, description, comment,
                        jsondata=None, image_file=None, pdf_file=None, code=None, data=None, datafile=None, datatype=None, mimetype=None, predecessors=[]):
    url = "http://localhost:5000/dobjs"
    # metadata = {
    #     'name': name,
    #     'owner_id': ownerid,
    #     'description': description,
    #     'comment': comment,
    #     'datatype': '/datatypes/json',
    #     'jsondata': jsondata,
    #     'mimetype': 'application/json',
    #     'predecessors': predecessors,
    # }
    #
    # files = {}
    # if image_file:
    #     metadata['datatype'] = '/datatypes/img'
    #     metadata['mimetype'] = 'image/jpg'
    #     files = {'imgpath': (image_file, open(image_file,'rb'), 'image/jpg')}
    # elif pdf_file:
    #     metadata['datatype'] = '/datatypes/pdf'
    #     metadata['mimetype'] = 'application/pdf'
    #     files = {'pdfpath': (pdf_file, open(pdf_file,'rb'), 'application/pdf')}
    # el

    metadata = {
        'name': name,
        'owner_id': ownerid,
        'description': description,
        'comment': comment,
        'datatype': datatype,
        'data': data,
        'mimetype': mimetype,
        'predecessors': predecessors,
    }

    if code:
        metadata['datatype'] = '/datatypes/function'
        metadata['mimetype'] = 'text/plain'
        metadata['code'] = code

    files = {}
    if datafile:
        files = {'datafile': open(datafile,'rb')}

    files['metadata'] = json.dumps(metadata)

    response = requests.post(url, files=files)
    obj_data = response.json()

    return obj_data

def update_data_object(objectid, ownerid, comment, jsondata=None, image_file=None, pdf_file=None, code=None, data=None, datafile=None, datatype=None, mimetype=None,predecessors=[]):
    url = "http://localhost:5000/versions"
    metadata = {
            'owner_id': ownerid,
            'dobj_id': objectid,
            'comment': comment,
            'datatype': '/datatypes/json',
            'mimetype': 'application/json',
            'jsondata': jsondata,
            'predecessors': predecessors,
        }

    files = {}
    if datafile:
        files = {'datafile': open(datafile,'rb')}

    if code:
        metadata['datatype'] = '/datatypes/function'
        metadata['mimetype'] = 'text/plain'
        metadata['code'] = code
    elif image_file:
        metadata['datatype'] = '/datatypes/img'
        metadata['mimetype'] = 'image/jpg'
        files = {'imgpath': (image_file, open(image_file,'rb'), 'image/jpg')}
    elif pdf_file:
        metadata['datatype'] = '/datatypes/pdf'
        metadata['mimetype'] = 'application/pdf'
        files = {'pdfpath': (pdf_file, open(pdf_file,'rb'), 'application/pdf')}

    files['metadata'] = json.dumps(metadata)

    response = requests.post(url, files=files)

    obj_data = response.json()
    return obj_data

        # function_id = full_text_xml,
        # dataobject_id = dobjid
        # name = 'XML Full Text for PDF b4e98770894089e276f91c1d00e58c8885708e11',
        # ownerid = user_id,
        # description = 'XML-formatted full text parse',
        # comment = 'PDF: b4e98770894089e276f91c1d00e58c8885708e11'

def apply_function(function_id, dataobject_id, ownerid, name, description, datatype, comment):
    url = "http://localhost:5000/function/{}/{}".format(function_id, dataobject_id)

    mimetypes = {
        '/datatypes/json': 'application/json',
        '/datatypes/xml': 'application/xml',
    }

    metadata = {
            'owner_id': ownerid,
            'dobj_id': dataobject_id,
            'func_id': comment,
            'datatype': datatype,
            'mimetype': mimetypes.get(datatype, 'text/plain'),
            'name': name,
            'description': description,
            'comment': comment
        }
    files = {'metadata': json.dumps(metadata)}
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
