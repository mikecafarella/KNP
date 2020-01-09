
import pandas as pd
import utils

def kgpcompile(action, KG_references, web=False):

    # Sanitiy check on Action
    # if(action not in traits_utils.Actions):
    #     raise ValueError("Unknown action!")

    # Turn each parameter into its corresponding ID in Wikidata
    if not web:
        IDs = utils.KG_references_to_ID(KG_references)
    else:
        IDs = []
        for param in KG_references:
            IDs.append(param.split("."))
            IDs[-1] = [x[0:x.find(":")] for x in IDs[-1]]
        

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

    return (IDs, KG_references, method, refinements, parameter_transformers, mapping, KG_tables)


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


def compute_quality_metrics(action, IDs, KP, method, refinements, parameter_transformers, mapping, KG_tables):
    ## evaluation_results = {refinement: {constraint_1: True, constraint_2: True...}....}
    total_valid_constraint_count, total_invalid_constraint_count = 0, 0
    evaluation_results = {}
    for refinement in refinements:
        evaluation_result = refinement.evaluate(action, IDs, method, mapping, KG_tables, parameter_transformers)
        evaluation_results[str(refinement)] = evaluation_result
        total_valid_constraint_count += list(evaluation_result.values()).count(True)
        total_invalid_constraint_count += list(evaluation_result.values()).count(False)


    utils.log_msg("Total satisfied constraint count is {}, total unsatisfied constraint count is {}".format(total_valid_constraint_count, total_invalid_constraint_count))

    return (evaluation_results, total_valid_constraint_count, total_invalid_constraint_count)

    
    

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
    action = args.KP[0]
    KG_references = args.KP[1:]

    IDs, KP, method, refinements, parameter_transformers, mapping, KG_table = kgpcompile(action, KG_references)

    # Computue quality
    metrics = compute_quality_metrics(action, IDs, KP, method, refinements, parameter_transformers, mapping, KG_table)
    if metrics[-1]:
        raise ValueError("There is unsatisfied constraints. Don't execute.")

    user_facing_result = execute_compiled_program(mapping, KG_table, parameter_transformers, method)




