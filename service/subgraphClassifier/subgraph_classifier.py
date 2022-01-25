# takes in objects to classify
def get_label(file_objects, subgraph_root_id):

    output = None
    for file_props_dict in file_objects:
        if 'ObservedFile' in file_props_dict:
            if file_props_dict['ObservedFile']['uuid'] == subgraph_root_id:
                output = file_props_dict
                break
    inputs = {}
    for file_props_dict in file_objects:
        if file_props_dict != output:
            if 'ObservedFile' in file_props_dict:
                inputs.setdefault('input_files', [])
                inputs['input_files'].append(file_props_dict)
            else:
                # must be an observed process
                inputs.setdefault('observed_process', [])
                inputs['observed_process'].append(file_props_dict)

    labels = []    
    if len(inputs['input_files']) == 1 and inputs['input_files'][0]['ByteSet'] == output['ByteSet']:
        labels.append("Sharing event from {} to {}".format(inputs['input_files'][0]['ObservedFile']['username'], output['ObservedFile']['username']))
    elif len(inputs['input_files']) == 1 and len(inputs['observed_process']) == 1 and inputs['observed_process'][0]['ObservedProcess']['name'] == 'Word':
        labels.append("Used Microsoft Word to do something")

    return labels
