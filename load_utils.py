import time
import ujson as json

time1 = time.time()
label_desc_dict = {}
with open('label_desc.txt', 'rt') as json_file:
    label_desc_dict = json.load(json_file)
print(time.time()-time1)

def merge_dicts(dic1, dic2):
    for key, value in dic2.items():
        if key not in dic1:
            dic1[key] = value
        else:
            if isinstance(value, list) and isinstance(value, list):
                dic1[key] += value
            elif isinstance(value, list):
                dic1[key] = value.append(dic1[key])
            elif isinstance(dic1[key], list):
                dic1[key].append(value)
            else:
                dic1[key] = [dic1[key], value]
    return dic1

def parse_wikidata_datavalue(datavalue, datatype: str):
    """
        Args:
        datavalue (dict): a wikidata datavalue.
        datatype: wikidata datatype.

        Return:
            A dict represensts a row of data in the final DataFrame.
    """
    rst = {}
    if datatype == 'wikibase-item':
        assert(datavalue['type'] == 'wikibase-entityid')
        # rst = {"wikidatadata ID": datavalue['value']["id"]}
        # item = search_entity(datavalue['value']["id"], "item", limit=1)[0]
        # rst = {"wikidata ID": item["id"], "wikidata entity type": "item", "label": item.get("label"), "description": item.get("description"), "aliases": item.get("aliases"), "url": item["url"][2:]}
        try:
            rst = {"wikidata ID": datavalue['value']["id"], "wikidata entity type": "item", "label": label_desc_dict[datavalue['value']["id"]][0],
                   "description": label_desc_dict[datavalue['value']["id"]][1]}
        except KeyError:
            rst = {}
    elif datatype == 'wikibase-property':
        assert(datavalue['type'] == 'wikibase-entityid')
        # property = search_entity(datavalue['value']["id"], "property", limit=1)[0]
        # rst = {"wikidata ID": property["id"], "wikidata entity type": "property", "label": property.get("label"), "description": property.get("description"), "aliases": property.get("aliases"), "url": property["url"][2:]}
        rst = {"wikidata ID": datavalue['value']["id"], "wikidata entity type": "property", "label": label_desc_dict[datavalue['value']["id"]][0],
               "description": label_desc_dict[datavalue['value']["id"]][1]}
    elif datatype == 'commonsMedia':
        #
        assert(datavalue['type'] == 'string')
        rst = {"url": datavalue["value"]}
    elif datatype == 'globe-coordinate':
        assert(datavalue['type'] == 'globecoordinate')
        rst = datavalue['value']
    elif datatype == 'string':
        assert(datavalue['type'] == 'string')
        rst = {"value": datavalue["value"]}
    elif datatype == 'monolingualtext':
        assert(datavalue['type'] == 'monolingualtext')
        rst = datavalue["value"]
    elif datatype == 'external-id':
        #
        assert(datavalue['type'] == 'string')
        rst = {"value": datavalue["value"]}
    elif datatype == 'quantity':
        assert(datavalue['type'] == 'quantity')
        rst = datavalue["value"]
    elif datatype == 'time':
        assert(datavalue['type'] == 'time')
        rst = datavalue["value"]
        # value = datavalue["value"]
        # return {"time": value.get('time'), "timezone": value.get('timezone'), "before": value.get('before'), "after": value.get('after'), "precision":value.get('precision'), "calendermodel": value.get('calendermodel')}
    elif datatype == 'url':
        #
        assert(datavalue['type'] == 'string')
        rst = {"url": datavalue["value"]}
    elif datatype == 'math':
        #
        assert(datavalue['type'] == 'string')
        rst = {"url": datavalue["value"]}
    elif datatype == 'geo-shape':
        pass
    elif datatype == 'tabular-data':
        # Documentation here: https://www.mediawiki.org/wiki/Help:Tabular_Data
        # Too complex
        pass
    elif datatype == 'wikibase-lexeme':
        pass
    elif datatype == 'wikibase-form':
        pass
    elif datatype == 'wikibase-sense':
        pass
    else:
        # raise ValueError("Unknown datatype {}!".format(datatype))
        pass
    #
    # make values in rst become a list, so later rst can be used to build a DataFrame
    #
    return rst


def parse_wikidata_qualifiers(qualifiers):
    """
        Args:
            qualifiers (dict): Property_ID ==> a list of snaks
        Returns:
            A dict.
    """
    if qualifiers is None:
        return {}
    rst = {}
    for property_id, snaks in qualifiers.items():
        # property = search_entity(property_id, "property", limit=1)[0]['label']
        key_prefix = property_id + ":" + label_desc_dict[property_id][0] + "."
        for snak in snaks:
            datatype = snak.get("datatype")
            datavalue = snak.get("datavalue")
            if datatype is None or datavalue is None:
                continue
            dic = parse_wikidata_datavalue(datavalue, datatype)
            #
            # add prefix to keys
            #
            dic = {key_prefix+k: v for k, v in dic.items()}
            rst = merge_dicts(rst, dic)
    return rst
