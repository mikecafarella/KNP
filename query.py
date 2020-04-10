import utils
from wikidata_utils import *
from typing import List, Set, Mapping, Tuple
import pandas as pd

class IR:
    """ The Intermidiate Representation for an entity (item/property). Supported KGs: Wikidata

        Args:
            entity_id: the entity ID.
            focus: the part of the IR that is built. 
                E.g., For Q30.GDP, we build an IR for Q30 with only GDP property data fetched.
        
        Attributes:
            type (str): item / property. Others are not supported yet.
            id (str)
            focus (str): The property_id of the IT 
            desc (str)
            aliases (List[str])
            properties (Dict): Keys are property_id, values are DataFrame
    """ 
    def __init__(self, entity_id: str, KG: str, focus: str=None):
        if KG.lower() != "wikidata":
            raise ValueError("Unsupported KG: {}".format(KG))
        self.KG = KG
        self.id = entity_id
        self.focus = focus
        self.focus_label = None
        self.properties = {}

        if entity_id.startswith("Q"):
            self.type = "item"
        elif entity_id.startswith("P"):
            self.type = "property"
        else:
            raise ValueError("Unsupported entity type with id = {}".format(entity_id))
        self._generate_IR_()
        
    def _generate_IR_(self):
        entity_obj = get_entity(self.id)
        self.label = entity_obj["labels"].get("en", {}).get("value")
        self.desc = entity_obj["descriptions"].get("en", {}).get("value")
        self.aliases = [m["value"] for m in entity_obj["aliases"]["en"]]
        if self.focus is not None:
            p = search_entity(self.focus, 'property', limit=1)[0]
            self.focus_label = p.get("label")
        for property_id, snaks in entity_obj['claims'].items():
            # property = search_entity(property_id, 'property', limit=1)[0]
            if self.focus and property_id != self.focus:
                continue
            data_df = None
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
                #
                # Assume no overlapping keys in qualifiers_maping and value_mapping
                #
                assert(set(value_mapping.keys()) != set(qualifiers_mapping.keys()))
                value_mapping.update(qualifiers_mapping)
                #
                # Add prefix to all keys
                #
                # key_prefix = self.label + "." + 
                # value_mapping = {key_prefix+k: v for k, v in value_mapping.items()}
                
                if data_df is None:
                    data_df = pd.DataFrame.from_records([value_mapping])
                else:
                    data_df = data_df.append(value_mapping, ignore_index=True, sort=True)
                # print(data_df)
            #
            # Open question: do we want to include property labels in keys?
            #
            self.properties[property_id] = data_df


    def __getitem__(self, key):
        return self.properties.get(key)

    def __str__(self):
        if self.focus is None:
            return self.KG + ": " + self.id + "({})".format(self.label)
        else:
            return self.KG + ": " + self.id + "({})".format(self.label) + ".{}({})".format(self.focus, self.focus_label)


class Query:
    """ The class for user queries.

        Args:
            raw_query (string): the raw string the user typed.

        Attributes:
            raw_query: the raw string the user typed.
            operator_desc (str): A string describes the task, could be used to match Refinements.
            pos_args (list): positinal arguments in the query.
            keyword_args (list): keyword arguments in the query.
            KG_params (List): a list of IR.
    """
    def __init__(self, raw_query, KG):
        self.raw_query = raw_query
        self._parse_user_query_()
        self.KG = KG
        #
        # Generates IRs
        #
        self._data_preprocess_()
    
    def _parse_user_query_(self):
        """
        Fow now: assume the user uses a dataset from seaborn by passing the dataset name
            as the first argument in the query string.
        """
        operator_desc, first_params, pos_args, keyword_args = utils.parse(self.raw_query)
        self.operator_desc = operator_desc
        self.pos_args = pos_args
        self.keyword_args = keyword_args
        self._first_params = first_params
        # if KG is None:
        #     self.datasets = [utils.load_seaborn_dataset(dataset_name) for dataset_name in first_params]
        # else:
        #     self.KG_params = first_params

    def _data_preprocess_(self):
        """
            Converts KG_params to IRs.

            Args:
                KG_params: A list of expressions referring to KG data.
                        -- An entity (whether the user refers to it directly, as in Q76, or via an expression, as in Q1048.P19) 
                        -- Others (E.g., Q76.P569)
        """
        KG_params = {}
        if self.KG and self.KG.lower() == "wikidata":
            for KG_param in self._first_params:
                entity_id = KG_param.split(".")[0]
                if "." in KG_param:
                    # expression = A.B
                    property_id = KG_param.split(".")[1]
                    claims = get_claims(entity_id, property_id)
                    if claims is None:
                        raise ValueError("No result for {}".format(KG_param))
                    #
                    # Check if the expression refers to another entity.
                    #
                    type = claims[0]["mainsnak"].get('datatype')  # TODO: expr refers to a list of entities?
                    if type is None:
                        # No datavalue
                        KG_params[KG_param] = None
                        continue
                    elif type == "wikibase-item" or type == "wikibase-property":
                        new_entity_id = claims[0]["mainsnak"]["datavalue"]["value"]["id"]
                        KG_params[KG_param] = IR(new_entity_id, self.KG)
                    else:
                        KG_params[KG_param] = IR(entity_id, self.KG, focus=property_id)
                else:
                    # expr = A
                    KG_params[KG_param] = IR(entity_id, self.KG)
        else:
            raise ValueError("Unsupported KG: {}".format(KG))
        self.KG_params = KG_params
    
    def __getitem__(self, key):
        return self.KG_params.get(key)