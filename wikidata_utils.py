import requests
import pandas as pd
from pandas.io.json import json_normalize
import json

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
        rst.append(i['id'])
    return rst

def get_entity(entity_id):
    params = {
        'action': 'wbgetentities',
        'format': 'json',
        'languages': 'en',
        'ids': entity_id
    }
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

def KG_data_to_dataset(KG_data):
    """Transform KG data to a 'dataset'."""
    raw_data = KG_data
    # raw_data is a list of snaks
    for i in range(len(raw_data)):
        raw_data[i].pop('references', None)
        raw_data[i].pop('qualifiers-order', None)
        raw_data[i].pop('type', None)
        raw_data[i].pop('rank', None)
        # raw_data[i].pop('id', None)

    data_frame = json_normalize(raw_data)
    # print(data_frame.columns)
    # print(data_frame)
    data_frame = explode(data_frame)
    # print(data_frame)
    data_frame = flatten_dict(data_frame)
    # print(data_frame)
    return data_frame        

def explode(data_frame):
    """Iterate all columns, and explode them if needed."""
    for column in data_frame:
        if(isinstance(data_frame[column].values[0], list) or (column.startswith("qualifiers.") and len(column.split("."))==2)):
            data_frame = data_frame.explode(column).reset_index(drop=True)
    return data_frame

def flatten_dict(data_frame):
    for column in data_frame:
        if(isinstance(data_frame[column].values[0], dict)):
            tmp = json_normalize(data_frame[column].values[0], errors='ignore').add_prefix(column + ".")
            for x in data_frame[column].values[1:]:
                if(isinstance(x, dict)):
                    t = json_normalize(x, errors='ignore').add_prefix(column + ".")
                    tmp = pd.concat([tmp, t], sort=True)
            tmp = tmp.reset_index(drop=True)
            data_frame = data_frame.drop(columns=[column], axis=1)
            data_frame = pd.concat([data_frame, tmp], axis=1, sort=True)
    return data_frame

def get_link(KG_param):
    """Get the webgetclaims or webgetentities api link for the KG_param, which is in the form "ID:label.ID:label"."""
    if "." not in KG_param:
        # Get entity
        ID = KG_param[0:KG_param.find(":")]
        return "https://www.wikidata.org/w/api.php?action=wbgetentities&ids={}&languages=en".format(ID)
    else:
        item_ID = KG_param[0:KG_param.find(":")]
        property_ID = KG_param[KG_param.find(".") + 1:KG_param.find(":", KG_param.find(".") + 1)]
        return "https://www.wikidata.org/w/api.php?action=wbgetclaims&entity={}&property={}&languages=en".format(item_ID, property_ID)