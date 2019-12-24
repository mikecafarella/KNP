def log_msg(msg):
    print("log: " + msg)

import pandas as pd
def kgpcompile(args):

    action = args.KP[0]
    KG_references = args.KP[1:]

    # Sanitiy check on Action
    # if(action not in traits_utils.Actions):
    #     raise ValueError("Unknown action!")

    # Turn each parameter into its corresponding ID in Wikidata
    IDs = utils.KG_references_to_ID(KG_references)

    # Get the corresponding data
    KG_data = utils.get_KG_data(IDs)

    # Flatten the KG data into "Dataset" and "Entity"
    KG_datasets_and_entities = []
    for data in KG_data:
        if(data['type'] == 'claims'):
            KG_datasets_and_entities.append(utils.Dataset(data['data'], data['user_code']))
        elif(data['type'] == 'entity'):
            KG_datasets_and_entities.append(utils.Entity(data['data'], data['user_code']))
    # print(KG_datasets_and_entities[0].data_frame.columns)
    # print(KG_datasets_and_entities[0].data_frame['mainsnak.datavalue.value.amount'])

    # Get the concrete method
    method = utils.get_method()  # TODO fill in function parameters

    # Get refinements
    refinements = utils.get_refinements()  # TODO fill in function parameters

    # Slot mapping
    slot_maping = utils.get_slot_mapping(action, method, KG_datasets_and_entities)

    # Transform KG dataset to fit into the slots
    parameter_transformers = utils.get_parameter_transformers(slot_maping)


    return (args.KP, method, refinements, parameter_transformers)


if __name__ == '__main__':
    import argparse
    import os
    import json
    import random
    import utils

    # Take user code
    parser = argparse.ArgumentParser(description="Takes in a knowledge program, and execute.")
    parser.add_argument('KP', nargs='+', help="The knowledge program, surround an argument by '' if there is space in it.")
    args = parser.parse_args()
    
    compiled_program = kgpcompile(args)
