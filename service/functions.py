KNPS_URL = "http://localhost:5000"
import requests
import base64
import sys
import types
import json
from helpers import *

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

def get_dobj(dobj_id):
    return get_dobj_contents(dobj_id)

def execute_function(func_id, inputs, params=[]):
    code = get_dobj_contents(func_id)

    if type(code) != str:
        # TODO: Figure out why the code get mangled like this. Happens when uploading via API
        code = code.decode().replace("\\n", "\n").strip('"').replace('\\"','"')


    g = {}
    l = {}

    exec(code, globals(), l)

    for name, func in l.items():
        pass

    if len(inputs) == 1:
        inputs = inputs[0]

    if len(params):
        return func(inputs, params)
    else:
        return func(inputs)
