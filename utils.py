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
        self.user_code = user_code
        self.raw_data = KG_data
        self.id = KG_data['id']
        self.label = KG_data['labels']['en']['value']
        self.description = KG_data['descriptions']['en']['value']
        self.properties = {}
        for pid, snaks in KG_data['claims'].items():
            self.properties[pid] = Dataset(snaks)


def KG_references_to_ID(KG_references):
    rst = []
    for i in range(len(KG_references)):
        split_arg = KG_references[i].split('.')
        rst.append([wu.search_entity(split_arg[0], 'item', limit=1)[0]])
        for j in range(1, len(split_arg)):
            rst[i].append(wu.search_entity(split_arg[j], 'property', limit=1)[0])
    return rst


def get_KG_data(IDs):
    data = []
    for ID in IDs:
        if(None in ID):
            raise ValueError("None in IDs!")
        if(len(ID) == 1):
            data.append({'data': wu.get_entity(ID[0]), 'type': 'entity'})
        elif(len(ID) == 2):
            data.append({'data': wu.get_claims(ID[0], ID[1]), 'type': 'claims'})
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

def get_slot_mapping(action, method, KG_datasets_and_entities, KG_references):
    # TODO

    # All avialable fields in the KG data
    KG_params = {}
    for data in KG_datasets_and_entities:
        user_code = data.user_code
        if(isinstance(data, Entity)):
            for pid in data.properties:
                for column in data.properties[pid].data_frame.columns:
                    KG_params[".".join([user_code, pid, column])] = data.properties[pid].data_frame[column].values
        elif(isinstance(data, Dataset)):
            for column in data.data_frame.columns:
                KG_params[".".join([user_code, column])] = data.data_frame[column].values
        else:
            raise ValueError("Impossible data, neither entity nor dataset!")
    
    # print("Avaliable KG data:")
    # print(list(KG_params.keys()))

    # The slot mapping
    num_args = method.num_args
    arg_1 = KG_params["Canada.GDP.mainsnak.datavalue.value.amount"]
    arg_2 = KG_params["Canada.GDP.qualifiers.P585.datavalue.value.time"]
    arg_3 = "time"
    arg_4 = "Canada.GDP"
    mapped_data = [arg_1, arg_2, arg_3, arg_4]
    return mapped_data

def get_parameter_transformers(mapped_data, method):

    # type_checks = method.type_checks TODO

    transformers = []
    for arg in mapped_data:
        pass
    # hard-code
    transformers = [lambda x: x, lambda x: x,lambda x: x, lambda x: x]
    return transformers