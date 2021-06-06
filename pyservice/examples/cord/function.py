KNPS_URL = "http://localhost:5000"
import requests
import base64
import * from helpers

def get_dobj_contents(dobj_id):
    url = "{}/dobjs/{}".format(KNPS_URL, dobj_id)
    response = requests.get(url)
    obj_data = response.json()
    version_id = obj_data['versions'][0]['id']

    url = "{}/version/{}".format(KNPS_URL, version_id)
    response = requests.get(url)
    version_data = response.json()

    if version_data['contents']['mimetype'] == 'application/json':
        data = json.loads(base64.b64decode(version_data['contents']['contents']))
    else:
        data = base64.b64decode(version_data['contents']['contents'])

    return data

def full_text_process(dobj_id):
   import requests
   url = 'http://s2-grobid-tokens.us-west-2.elasticbeanstalk.com/api/processFulltextDocument'
   input_data = get_dobj_contents(dobj_id)
   files = {'input': input_data}
   r = requests.post(url, files=files)
   return r.text

def pdf_structure(dobj_id):
   import requests
   url = 'http://s2-grobid-tokens.us-west-2.elasticbeanstalk.com/api/processPdfStructure'
   input_data = get_dobj_contents(dobj_id)
   files = {'input': input_data}
   r = requests.post(url, files=files)
   return r.json()

filename = 'pdfs/276d1d1c20336ca2a6f54c7a95507001917e4c44.pdf'
