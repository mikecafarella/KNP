import wikidata_utils as wu
import json
import methods
import refinements
from datetime import datetime
import iso8601
import pandas as pd


_KG = 'WikiData'


def log_msg(msg):
    print("log: " + msg)


class Dataset(dict):
    def __init__(self, KG_data, user_code=None):
        self.raw_data = KG_data
        self.user_code = user_code
        self.data_frame = wu.KG_data_to_dataset(KG_data)  # should be a DataFrame
    
    def __getitem__(self, column):
        if(column == "columns"):
            return self.data_frame.columns
        return self.data_frame[column]
    

class Entity(dict):
    def __init__(self, KG_data, user_code):
        self.user_code = user_code
        self.raw_data = KG_data
        self.id = KG_data['id']
        self.label = KG_data['labels']['en']['value']
        self.description = KG_data['descriptions']['en']['value']
        self.properties = {}
        for pid, snaks in KG_data['claims'].items():
            self.properties[pid] = Dataset(snaks)
    
    def __getitem__(self, pid):
        return self.properties[pid]


def KG_references_to_ID(KG_references):
    """Default get the first one in the returned result."""
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
    method = methods.PlotTwoLines()
    log_msg("The picked concrete method is {}.".format(type(method).__name__))
    return method


def get_refinements():
    """Returns a tuple of Refinements."""
    # TODO
    log_msg("The picked refinements are {}.".format(" ".join(((str(refinements.ComparingGDP()), )))))
    return (refinements.ComparingGDP(), )

def get_slot_mapping(action, method, KG_datasets_and_entities, KG_references):
    # TODO

    # All avialable fields in the KG data. KG_tables[user_code]
    KG_tables = {}
    for data in KG_datasets_and_entities:
        user_code = data.user_code
        KG_tables[user_code] = data

    # The slot mapping
    mapping = {}
    mapping["x_value_1"] = (KG_references[0], "qualifiers.P585.datavalue.value.time", True)
    mapping["y_value_1"] = (KG_references[0], "mainsnak.datavalue.value.amount", True)
    mapping["legend_1"] = (KG_references[0], False)
    mapping["x_value_2"] = (KG_references[1], "qualifiers.P585.datavalue.value.time", True)
    mapping["y_value_2"] = (KG_references[1], "mainsnak.datavalue.value.amount", True)
    mapping["legend_2"] = (KG_references[1], False)
    mapping["xlabel"] = ("time", False)
    mapping["ylabel"] = ("GDP", False)
    
    return (KG_tables, mapping)

def get_parameter_transformers(mapping, method):

    transformers = {}

    # hard-code
    transformers["x_value_1"] = "lambda l:[iso8601.parse_date(x[1:]).year for x in l]"
    transformers["y_value_1"] = "lambda l: [float(x) for x in l]"
    transformers["legend_1"] = "lambda x: x"
    transformers["x_value_2"] = "lambda l:[iso8601.parse_date(x[1:]).year for x in l]"
    transformers["y_value_2"] = "lambda l: [float(x) for x in l]"
    transformers["legend_2"] = "lambda x: x"
    transformers["xlabel"] = "lambda x: x"
    transformers["ylabel"] = "lambda x: x"

    return transformers

def get_method_by_name(method_name):
    return getattr(methods, method_name)
