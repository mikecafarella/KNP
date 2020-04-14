import requests
from pandas.io.json import json_normalize
from typing import List, Set, Mapping, Tuple
import pandas as pd
import json

import socket

socket.setdefaulttimeout(1)

_API_ROOT = "https://www.wikidata.org/w/api.php"

def search_entity(search_string, type, limit=10):
    """Search for a entity."""
    params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'language': 'en',
        'search': search_string,
        'limit': limit,
        'type': type
    }
    info = requests.get(_API_ROOT, params=params).json()['search']
    rst = []
    for _, i in enumerate(info):
        rst.append(i)
    return rst

def get_entity(entity_id):
    params = {
        'action': 'wbgetentities',
        'format': 'json',
        'languages': 'en',
        'ids': entity_id
    }
    #tmpResult = requests.get(_API_ROOT, params=params).json()
    #print("TMP", tmpResult)
    return requests.get(_API_ROOT, params=params).json()['entities'][entity_id]


def get_claims(entity_id, property_id=None):
    """Get claims for an item or a property."""
    params = {
        'action': 'wbgetclaims',
        'format': 'json',
        'entity': entity_id
    }
    if(property_id):
        params['property'] = property_id
    
    claims = requests.get(_API_ROOT, params=params).json()
    if('error') in claims:
        raise ValueError(claims['error']['info'])
    if(not property_id):
        return claims['claims']
    else:
        return claims['claims'].get(property_id)

def get_qualifiers_datavalues(entity_id, property_id, qualifier_pid):
    """Get 'datavalue' of a qualifier for claims."""
    claims = get_claims(entity_id, property_id)
    values = claims[property_id]
    return get_qualifiers_datavalues_from_snaks(values, qualifier_pid)

def get_qualifiers_datavalues_from_snaks(snaks, qualifier_pid):
    return [snak['qualifiers'][qualifier_pid][0]['datavalue'] for snak in snaks]
    # TODO fix for a certain property of qualifers that has more than one snaks
    # skip for now

def get_mainsnak_datavalues_from_snaks(snaks):
    """snaks = [{'mainsnak':{'datavalue'}}, {}]."""
    return [snak['mainsnak']['datavalue'] for snak in snaks]

def get_datavalues_for_a_property(data, property_id):
    # data can be {"id":, "labels":} or [{'mainsnak':{'datavalue'}}, {}]
    if(not len(data)):
        raise ValueError("Data is empty!")
    try:
        if('claims' in data):
            ### data is a entity
            snaks = data['claims'][property_id]
            # print(snaks)
            return get_datavalues_for_a_property(snaks, property_id)
        elif(data[0]['mainsnak']['property'] == property_id):
            # data = [{'mainsnak':{'datavalue'}}, {}]
            return get_mainsnak_datavalues_from_snaks(data)
        else:
            # look at qualifiers
            return get_qualifiers_datavalues_from_snaks(data, property_id)
    except:
        return None

        

def get_value_from_datavalue(datavalues):
    # datavalues should be of type list/tuple
    # print(type(datavalues))
    rst = []
    for datavalue in datavalues:
        # print(datavalue)
        if(datavalue['type'] == "wikibase-entityid"):
            rst.append(datavalue['value']['id'])
        elif(datavalue['type'] == 'time'):
            rst.append(datavalue['value']['time'])
        elif(datavalue['type'] == 'quantity'):
            rst.append(datavalue['value']['amount'])
    return rst


# def explode(data_frame):
#     """Iterate all columns, and explode them if needed."""
#     for column in data_frame:
#         if(isinstance(data_frame[column].values[0], list) or (column.startswith("qualifiers.") and len(column.split("."))==2)):
#             data_frame = data_frame.explode(column).reset_index(drop=True)
#     return data_frame

# def flatten_dict(data_frame):
#     for column in data_frame:
#         if(isinstance(data_frame[column].values[0], dict)):
#             tmp = json_normalize(data_frame[column].values[0], errors='ignore').add_prefix(column + ".")
#             for x in data_frame[column].values[1:]:
#                 if(isinstance(x, dict)):
#                     t = json_normalize(x, errors='ignore').add_prefix(column + ".")
#                     tmp = pd.concat([tmp, t], sort=True)
#             tmp = tmp.reset_index(drop=True)
#             data_frame = data_frame.drop(columns=[column], axis=1)
#             data_frame = pd.concat([data_frame, tmp], axis=1, sort=True)
#     return data_frame
