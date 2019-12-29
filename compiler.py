
import pandas as pd
import utils

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
    for i in range(len(KG_data)):
        data = KG_data[i]
        if(data['type'] == 'claims'):
            KG_datasets_and_entities.append(utils.Dataset(data['data'], KG_references[i]))
        elif(data['type'] == 'entity'):
            KG_datasets_and_entities.append(utils.Entity(data['data'], KG_references[i]))
    # print(KG_datasets_and_entities[0].data_frame.columns)
    # print(KG_datasets_and_entities[0].data_frame['mainsnak.datavalue.value.amount'])

    # Get the concrete method
    method = utils.get_method()  # TODO fill in function parameters

    # Get refinements
    refinements = utils.get_refinements()  # TODO fill in function parameters

    # Slot mapping
    KG_tables, mapping = utils.get_slot_mapping(action, method, KG_datasets_and_entities, KG_references)

    # Transform KG dataset to fit into the slots
    parameter_transformers = utils.get_parameter_transformers(mapping, method)

    return (IDs, args.KP, method, refinements, parameter_transformers, mapping, KG_tables)


def execute_compiled_program(mapping, KG_tables, parameter_transformers, method):

    # Apply transformers onto the data
    transformed_mapped_data = []
    for i in range(len(parameter_transformers)):
        if(mapping[i][-1]):
            # Need to fetch the data from KG_tables
            data = KG_tables[mapping[i][0]][mapping[i][1]]
        else:
            data = mapping[i][0]
        transformed_mapped_data.append(parameter_transformers[i](data))

    return method.function(*transformed_mapped_data)


def compute_quality_metrics(IDs, KP, method, refinements, parameter_transformers, mapping, KG_tables):

    total_valid_constraint_count, total_invalid_constraint_count = 0, 0
    for refinement in refinements:
        valid_count, invalid_count = refinement.evaluate(IDs, method, mapping, KG_tables, parameter_transformers)
        total_valid_constraint_count += valid_count
        total_invalid_constraint_count += invalid_count
    utils.log_msg("Total satisfied constraint count is {}, total unsatisfied constraint count is {}".format(total_valid_constraint_count, total_invalid_constraint_count))
    if(total_invalid_constraint_count):
        raise ValueError("There is unsatisfied constraints. Don't execute.")

    
    

if __name__ == '__main__':
    import argparse
    import os
    import json
    import random

    # Take user code
    parser = argparse.ArgumentParser(description="Takes in a knowledge program, and execute.")
    parser.add_argument('KP', nargs='+', help="The knowledge program, surround an argument by '' if there is space in it.")
    args = parser.parse_args()
    
    # KGP compile
    IDs, KP, method, refinements, parameter_transformers, mapping, KG_table = kgpcompile(args)

    # Computue quality
    metrics = compute_quality_metrics(IDs, KP, method, refinements, parameter_transformers, mapping, KG_table)


    user_facing_result = execute_compiled_program(mapping, KG_table, parameter_transformers, method)




