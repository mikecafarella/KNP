import wikidata_utils as wu


def get_targets(targets, arguments, data):
    try:
        if(targets == 'last property of all arguments'):
            return [argument[-1] for argument in arguments]
        if(targets == "all arguments"):
            rst = []
            for argument_data in data:
                rst.extend(wu.get_datavalues_from_snaks(argument_data))
            return rst
        if(targets.startswith("all arguments") and "." in targets):
            property_id = targets.split(".")[1]
            rst = []
            for argument_data in data:
                rst.extend(wu.get_datavalues_for_a_property(argument_data, property_id))
            return wu.get_value_from_datavalue(rst)
    except:
        return None
         

def get_function(func_name):
    return getattr(functions, func_name)


def invoke_conditions_ok(invoke_conditions, arguments, data):
    for invoke_condition in invoke_conditions:
        targets = get_targets(invoke_condition['targets'], arguments, data)
        function = get_function(invoke_condition['function'])
        value = invoke_condition.get('value')
        if(not function(value, targets)):
            return False
    return True


if __name__ == '__main__':
    import argparse
    from traits import traits_utils
    from traits import functions 
    import os
    import json

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
        invoke_conditions = refinement_data['invoke conditions']
        if(not invoke_conditions_ok(invoke_conditions, arguments, data)):
            continue 
        print("{} check passed.".format(refinement))



