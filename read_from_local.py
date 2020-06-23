import time
import json
import numpy as np
import bz2
import utils


if __name__ == '__main__':
    start = time.time()
    list_time = []
    with bz2.open('../latest-all.json.bz2', 'rt') as f:
        start = time.time()
        f.read(2)
        count = 0
        for line in f:
            dic = {}
            dic["property"] = {}
            try:
                load_start = time.time()
                entity_obj = json.loads(line[:-2])
                list_time.append(time.time()-load_start)
                count += 1
            except json.decoder.JSONDecodeError:
                print("Error!")
                continue
            dic["entity_id"] = entity_obj["id"]
            print(id)
            dic["name"] = entity_obj["labels"].get("en", {}).get("value")
            dic["description"] = entity_obj["descriptions"].get("en", {}).get("value")
            for property_id, snaks in entity_obj['claims'].items():
                dictionary = None
                for snak in snaks:
                    mainsnak = snak.get("mainsnak")
                    qualifiers = snak.get("qualifiers")
                    if mainsnak['snaktype'] != "value":
                        continue
                    datatype = mainsnak["datatype"]
                    datavalue = mainsnak["datavalue"]
                    value_mapping = utils.parse_wikidata_datavalue(datavalue, datatype)
                    if len(value_mapping) == 0:
                        continue
                    qualifiers_mapping = utils.parse_wikidata_qualifiers(qualifiers)
                    assert (set(value_mapping.keys()) != set(qualifiers_mapping.keys()))
                    value_mapping.update(qualifiers_mapping)
                    if dictionary is None:
                        dictionary = value_mapping
                    else:
                        dictionary = dictionary.update(value_mapping)
                if dictionary is None:
                    dic["property"][property_id] = dictionary
                else:
                    dic["property"][property_id] = dictionary
            if count == 10:
                break
        print(np.mean(list_time))
        print(time.time()-start)
