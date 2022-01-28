import pandas
from sklearn.tree import DecisionTreeClassifier
import numpy as np
from io import StringIO
import base64
from data_gen import FILE_TYPE_NUMERICAL_MAP, get_data_set, LABEL_OPERATION_MAP, DATASET_NPZ_FILE 
from joblib import dump, load

CLF_NAME = 'knps_classifier.joblib'

def build_classifier(dump=False, load=False):
    if load:
        clf = load(CLF_NAME)
    else:
        X, y = get_data_set()
        clf = DecisionTreeClassifier()
        clf.fit(X, y)
    if dump:
        dump(clf, CLF_NAME)
    return clf

# extract feature from input from UI
def extract_features(node):
    node_type = node['ByteSet']['filetype']
    if node_type == 'text/csv':
        decoded_content = base64.b64decode(node['content'])
        df = pandas.read_csv(StringIO(str(decoded_content, encoding='utf-8')))
        cols = [col for col in df.columns if "Unnamed" not in col]
        return np.array([[FILE_TYPE_NUMERICAL_MAP[node_type], len(cols)]])
    else:
        return np.array([[FILE_TYPE_NUMERICAL_MAP[node_type], 0]])

def apply_classifier(arguments, subgraph_root_id, dump=False, load=False):
    individual_node_features = np.empty((0,2), int)
    output_node_features = np.empty((0,2), int)
    for node, depth in arguments:
        if node['ObservedFile']['uuid'] == subgraph_root_id:
            output_node_features = np.append(output_node_features, extract_features(node), axis=0)
        else:
            individual_node_features = np.append(individual_node_features, extract_features(node), axis=0)
    
    avg_input = np.mean(individual_node_features, axis=0)
    avg_output = np.mean(output_node_features, axis=0)
    x = np.concatenate((avg_input, avg_output), axis=0)
    clf = build_classifier(dump, load)
    res = clf.predict_proba([x])[0]
    classes = clf.classes_
    results = [(res[i], classes[i]) for i in range(len(res))]
    results.sort(key=lambda x: x[0], reverse=True)
    return [LABEL_OPERATION_MAP[int(label)] for _, label in results]


if __name__ == "__main__":
    pass
   