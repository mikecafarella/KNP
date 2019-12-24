import wikidata_utils as wu
import json
import methods
import refinements

_KG = 'WikiData'


class Dataset(object):
    def __init__(self, KG_data, user_code=None):
        self.raw_data = KG_data
        self.user_code = user_code
        self.data_frame = wu.KG_data_to_dataset(KG_data)  # should be a DataFrame

class Entity(object):
    def __init__(self, KG_data, user_code):
        self.raw_data = KG_data
        self.id = KG_data['id']
        self.label = KG_data['labels']['en']['value']
        self.description = KG_data['descriptions']['en']['value']
        self.properties = {}
        for pid, snaks in KG_data['claims'].items():
            self.properties[pid] = Dataset(snaks)
            # try:
            #     self.properties[pid] = Dataset(snaks)
            # except:
            #     print("error")
            #     print(json.dumps(snaks))
            # self.properties[pid] = Dataset(snaks)


def KG_references_to_ID(KG_references):
    for i in range(len(KG_references)):
        split_arg = KG_references[i].split('.')
        KG_references[i] = [wu.search_entity(split_arg[0], 'item', limit=1)[0]]
        for j in range(1, len(split_arg)):
            KG_references[i].append(wu.search_entity(split_arg[j], 'property', limit=1)[0])
    return KG_references


def get_KG_data(IDs):
    data = []
    for ID in IDs:
        if(None in ID):
            raise ValueError("None in IDs!")
        if(len(ID) == 1):
            data.append({'data': wu.get_entity(ID[0]), 'type': 'entity', 'user_code': ID[0]})
        elif(len(ID) == 2):
            data.append({'data': wu.get_claims(ID[0], ID[1]), 'type': 'claims', 'user_code': ID[0] + "." + ID[1]})
        else:
            raise ValueError('Not supporiting A.B.C yet!')
    return data

def get_method():
    """Returns a ConcreteMethod."""
    # TODO
    return methods.Plot()

def get_refinements():
    """Returns a tuple of Refinements."""
    # TODO
    return (refinements.ComparingTwoThings())

def get_slot_mapping(action, method, KG_datasets_and_entities):
    # TODO
    