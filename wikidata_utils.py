import requests


_API_ROOT = "https://www.wikidata.org/w/api.php"

def search_entity(search_string, type, limit=10):
    """Search for a property."""
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
