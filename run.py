import wikidata_utils as wu


def get_targets(targets, arguments, data):
    try:
        if(targets == 'last property of all arguments'):
            return [argument[-1] for argument in arguments]
        if(targets == "all arguments"):
            # get the datavalues
            rst = []
            for argument_data in data:
                rst.append(wu.get_mainsnak_datavalues_from_snaks(argument_data))
            return rst
        if(targets.startswith("all arguments") and "." in targets):
            # get the datavalues
            property_id = targets.split(".")[1]
            rst = []
            for argument_data in data:
                rst.append(wu.get_datavalues_for_a_property(argument_data, property_id))
            return rst
    except:
        return None
         

def get_function(func_name):
    return getattr(functions, func_name)

def pre_conditions_ok(pre_conditions, arguments, data):
    """Check pre-conditions of a trait."""
    for pre_condition in pre_conditions:
        targets = get_targets(pre_condition['targets'], arguments, data)
        function = get_function(pre_condition['function'])
        value = pre_condition.get('value')
        if(not function(value, targets)):
            return False
    return True

def modify(constraint, arguments, data):
    raise ValueError("Not implemented yet!")


def apply_constraints(constraints, arguments, data):
    """ Apply constraints of a trait."""
    for constraint in constraints:
        targets = get_targets(constraint['targets'], arguments, data)
        function = get_function(constraint['function'])
        value = constraint.get('value')
        if(not function(value, targets)):
            constraints, arguments, data = modify(constraint, arguments, data)
        log_msg("Constraint: <{}> is applied.".format(constraint['description']))
    return (arguments, data)


def continue_apply_traits(current_traits):
    if(len(current_traits) > 0):
        return False
    return True



def log_msg(msg):
    print("log: " + msg)


if __name__ == '__main__':
    import argparse
    from traits import traits_utils
    from traits import functions 
    import os
    import json
    import random

    parser = argparse.ArgumentParser(description="Takes in a knowledge program, and execute.")
    parser.add_argument('KP', nargs='+', help="The knowledge program, surround an argument by '' if there is space in it.")
    args = parser.parse_args()
    # print(args.KP)
    # assert(0)
    action = args.KP[0]
    arguments = args.KP[1:]

    ### For now, let's assume the arguments will be matched to the first item/property in the search result.

    # Turn each parameter into its corresponding ID in Wikidata
    for i in range(len(arguments)):
        split_arg = arguments[i].split('.')
        arguments[i] = [wu.search_entity(split_arg[0], 'item', limit=1)[0]]
        for j in range(1, len(split_arg)):
            arguments[i].append(wu.search_entity(split_arg[j], 'property', limit=1)[0])

    # print(arguments)
    # Get the corresponding data
    data = []
    for argument in arguments:
        if(None in argument):
            raise ValueError("None in arguments!")
        if(len(argument) == 1):
            data.append(wu.get_entity(argument[0]))
        elif(len(argument) == 2):
            # print(argument)
            data.append(wu.get_claims(argument[0], argument[1]))
        else:
            raise ValueError('Not supporiting A.B.C yet!')

    # Deal with action
    if(action not in traits_utils.Actions):
        raise ValueError("Unknown action!")
    
    # Scan refinements
    directory = "traits/refinements/{}".format(action)
    for refinement in os.listdir(directory):
        with open(os.path.join(directory, refinement), 'r') as f:
            refinement_data = json.load(f)
        refinement = refinement.split('.')[0]  # Get rid of .json, making output clear
        pre_conditions = refinement_data['pre-conditions']
        log_msg("Check {}'s pre-conditions.".format(refinement))
        if(not pre_conditions_ok(pre_conditions, arguments, data)):
            log_msg("{}'s pre-conditions are not met.".format(refinement))
            continue 
        log_msg("{}'s pre-conditions are met.".format(refinement))

        # Apply constraints of the refinement
        log_msg("Now apply constraints of {}.".format(refinement))
        constraints = refinement_data['constraints']
        arguments, data = apply_constraints(constraints, arguments, data)

        # Randomly pick logic_traits and policy_traits
        log_msg("Start randomly picking logic/policy traits....")
        picked_traits = set()
        contradicting_traits = set()

        while(continue_apply_traits(picked_traits) and len(picked_traits) + len(contradicting_traits) < len(traits_utils.Traits)):
            trait = traits_utils.Traits[random.randint(0, len(traits_utils.Traits) - 1)]
            while(trait in picked_traits or trait in contradicting_traits):
                trait = traits_utils.Traits[random.randint(0, len(traits_utils.Traits) - 1)]
            
            log_msg("{} is picked.".format(trait.split(".")[0]))
            with open(os.path.join('traits', trait), 'r') as f:
                trait_data = json.load(f)
            # print(trait_data)
            if(not pre_conditions_ok(trait_data['pre-conditions'], arguments, data)):
                log_msg("{}'s pre-conditions are not met.".format(trait.split(".")[0]))
                contradicting_traits.add(trait)
                continue
            log_msg("{}'s pre-conditions are met. Now apply its constraints.".format(trait.split(".")[0]))
            arguments, data = apply_constraints(trait_data['constraints'], arguments, data)
            picked_traits.add(trait)

        # Randomly pick output_traits
        log_msg("Start randomly picking output traits....")
        contradicting_traits = set()
        while(len(contradicting_traits) < len(traits_utils.Output_Traits)):
            trait = traits_utils.Output_Traits[random.randint(0, len(traits_utils.Output_Traits) - 1)]
            while(trait in contradicting_traits):
                trait = traits_utils.Output_Traits[random.randint(0, len(traits_utils.Output_Traits) - 1)]
            log_msg("{} is picked.".format(trait.split(".")[0]))
            with open(os.path.join('traits', trait), 'r') as f:
                trait_data = json.load(f)
            if(not pre_conditions_ok(trait_data['pre-conditions'], arguments, data)):
                log_msg("{}'s pre-conditions are not met.".format(trait.split(".")[0]))
                contradicting_traits.add(trait)
                continue
            log_msg("{}'s pre-conditions are met. Now produce output.".format(trait.split(".")[0]))
            break
        
        # prepare data for the output