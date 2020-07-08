import ast
import pandas as pd
import itertools
import more_itertools
import random
import inspect
import methods
import glob
import matplotlib.pyplot as plt
import ujson as json
import yaml
import string
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from wikidata_utils import search_entity
import time


def parse(source):
    """ Parse a raw user query."""
    call = ast.parse(source, "operator string", mode="eval").body
    # print(ast.dump(call))
    # l = compile(call.args[0], "", "eval")
    # l = ast.literal_eval(call.args[0])
    # print(l)
    # TODO: might be buggy
    return call.func.id, [elt.value if isinstance(elt, ast.Constant) else elt.id for elt in call.args[0].elts], \
         [arg.value if isinstance(arg, ast.Constant) else arg.id for arg in call.args[1:]], \
             [(keyword.arg, keyword.value.value) for keyword in call.keywords]


def load_seaborn_dataset(name, **kws):
    path = ("datasets/seaborn/{}.csv")
    full_path = path.format(name)
    df = pd.read_csv(full_path, **kws)
    if df.iloc[-1].isnull().all():
        df = df.iloc[:-1]

    # Set some columns as a categorical type with ordered levels

    if name == "tips":
        df["day"] = pd.Categorical(df["day"], ["Thur", "Fri", "Sat", "Sun"])
        df["sex"] = pd.Categorical(df["sex"], ["Male", "Female"])
        df["time"] = pd.Categorical(df["time"], ["Lunch", "Dinner"])
        df["smoker"] = pd.Categorical(df["smoker"], ["Yes", "No"])

    if name == "flights":
        df["month"] = pd.Categorical(df["month"], df.month.unique())

    if name == "exercise":
        df["time"] = pd.Categorical(df["time"], ["1 min", "15 min", "30 min"])
        df["kind"] = pd.Categorical(df["kind"], ["rest", "walking", "running"])
        df["diet"] = pd.Categorical(df["diet"], ["no fat", "low fat"])

    if name == "titanic":
        df["class"] = pd.Categorical(df["class"], ["First", "Second", "Third"])
        df["deck"] = pd.Categorical(df["deck"], list("ABCDEFG"))

    return df


def generate_mappings(variables, columns, num_rows, sample_size_of_slicing=6, seed=0):
    """A generator function that yields mappings.

    Args:
        variables (list) (length = n): List of variable names.
        columns (list) (length = d): List of column names.
        num_rows (int): Number of rows in the dataset.
        sample_size_of_slicing (int): number of samples with different slicing for a mapping.


    Yield:
        Each mapping starts with (start_index, end_index) followed by n tuples in the form of
        (True/False, column).
        True means the column name itself is mapped to the variable."""

    random.seed(seed)
    d = len(variables)
    if num_rows < 3:
        sample_size_of_slicing = int(num_rows * (num_rows + 1) / 2)

    # Expand the variables to contain True/False.
    columns = [(True, column) for column in columns] + [(False, column) for column in columns]

    for mapping in itertools.product(columns, repeat=d):
        # if all are column names, indice has no meaning
        if more_itertools.quantify(mapping, lambda m: m[0]) == d:
            yield ((), mapping)
        else:
            seen_index = set()
            for i in range(sample_size_of_slicing):
                index_start = random.randint(0, num_rows-1)
                index_end = random.randint(index_start, num_rows-1)
                index = (index_start, index_end)
                while index in seen_index:
                    index_start = random.randint(0, num_rows-1)
                    index_end = random.randint(index_start, num_rows)
                    index = (index_start, index_end)
                seen_index.add(index)
                yield (index, mapping)


def test_one_mapping(method, actual_mapping, criterion="runnable"):
    try:
        method.function(*actual_mapping)
        return True
    except:
        return False


def test_mappings(method, dataframe, criterion="runnable", output_path=None):
    """ Test the all the mappings with the criterion.

        Args:
            method: A ConcreteMethod.
            dataframe: A pandas.DataFrame.
            criterion: under what crierion a mapping is a good one.

        Output:
            Print the mappings that pass the criterion in the format of
            (index, mappings)."""

    columns = dataframe.columns
    variables = list(inspect.signature(method.function).parameters.keys())
    count_ok_mappings = 0
    count_total_mappings = 0
    for index, mapping in generate_mappings(variables, columns, len(dataframe.index)):
        count_total_mappings += 1
        if not len(index):  # variables all correspond to strings.
            actual_mapping = [ m[1] if m[0] else dataframe[m[1]] for m in mapping]
        else:
            actual_mapping = [ m[1] if m[0] else dataframe[m[1]][index[0]:index[1]] for m in mapping]

        print(index, mapping)
        if test_one_mapping(method, actual_mapping, criterion):
            count_ok_mappings += 1
            if output_path:
                with open(output_path, 'a') as f:
                    f.write(json.dumps((index, mapping)) + "\n")

            else:
                print(index, mapping)
            # break
        count_total_mappings += 1
    print(count_ok_mappings, count_total_mappings)


def test_mappings_for_seaborn(method, output_path=None):
    """Test mappings for all the seaborn datasets for the 'method'.

        Args:
            method: the ConcreteMethod.
            output_path: the output directory. If it's None, output are printed to stdout."""

    datasets = glob.glob("datasets/seaborn/*.csv")
    for dataset in datasets:
        dataset_name = dataset.split("/")[-1].split(".")[0]
        if dataset_name == 'brain_network':
            continue
        print("Start loading dataset {}".format(dataset_name))
        df = load_seaborn_dataset(dataset_name)
        if output_path:
            test_mappings(method, df, output_path="{}/{}_runnable_mappings.json".format(output_path, dataset_name))
        else:
            test_mappings(method, df)


def clean_string(text):
    sw = stopwords.words('english')
    text = ''.join([word for word in text if word not in string.punctuation])
    text = text.lower()
    text = ' '.join([word for word in text.split() if word not in sw])
    return text

def parse_wikidata_datavalue(datavalue, datatype: str):
    """
        Args:
        datavalue (dict): a wikidata datavalue.
        datatype: wikidata datatype.

        Return:
            A dict represensts a row of data in the final DataFrame.
    """
    rst = {}
    if datatype == 'wikibase-item':
        assert(datavalue['type'] == 'wikibase-entityid')
        # rst = {"wikidatadata ID": datavalue['value']["id"]}
        # item = search_entity(datavalue['value']["id"], "item", limit=1)[0]
        # rst = {"wikidata ID": item["id"], "wikidata entity type": "item", "label": item.get("label"), "description": item.get("description"), "aliases": item.get("aliases"), "url": item["url"][2:]}
        try:
            rst = {"wikidata ID": datavalue['value']["id"], "wikidata entity type": "item", "label": label_desc_dict[datavalue['value']["id"]][0],
                   "description": label_desc_dict[datavalue['value']["id"]][1]}
        except KeyError:
            rst = {}
    elif datatype == 'wikibase-property':
        assert(datavalue['type'] == 'wikibase-entityid')
        # property = search_entity(datavalue['value']["id"], "property", limit=1)[0]
        # rst = {"wikidata ID": property["id"], "wikidata entity type": "property", "label": property.get("label"), "description": property.get("description"), "aliases": property.get("aliases"), "url": property["url"][2:]}
        rst = {"wikidata ID": datavalue['value']["id"], "wikidata entity type": "property", "label": label_desc_dict[datavalue['value']["id"]][0],
               "description": label_desc_dict[datavalue['value']["id"]][1]}
    elif datatype == 'commonsMedia':
        #
        assert(datavalue['type'] == 'string')
        rst = {"url": datavalue["value"]}
    elif datatype == 'globe-coordinate':
        assert(datavalue['type'] == 'globecoordinate')
        rst = datavalue['value']
    elif datatype == 'string':
        assert(datavalue['type'] == 'string')
        rst = {"value": datavalue["value"]}
    elif datatype == 'monolingualtext':
        assert(datavalue['type'] == 'monolingualtext')
        rst = datavalue["value"]
    elif datatype == 'external-id':
        #
        assert(datavalue['type'] == 'string')
        rst = {"value": datavalue["value"]}
    elif datatype == 'quantity':
        assert(datavalue['type'] == 'quantity')
        rst = datavalue["value"]
    elif datatype == 'time':
        assert(datavalue['type'] == 'time')
        rst = datavalue["value"]
        # value = datavalue["value"]
        # return {"time": value.get('time'), "timezone": value.get('timezone'), "before": value.get('before'), "after": value.get('after'), "precision":value.get('precision'), "calendermodel": value.get('calendermodel')}
    elif datatype == 'url':
        #
        assert(datavalue['type'] == 'string')
        rst = {"url": datavalue["value"]}
    elif datatype == 'math':
        #
        assert(datavalue['type'] == 'string')
        rst = {"url": datavalue["value"]}
    elif datatype == 'geo-shape':
        pass
    elif datatype == 'tabular-data':
        # Documentation here: https://www.mediawiki.org/wiki/Help:Tabular_Data
        # Too complex
        pass
    elif datatype == 'wikibase-lexeme':
        pass
    elif datatype == 'wikibase-form':
        pass
    elif datatype == 'wikibase-sense':
        pass
    else:
        # raise ValueError("Unknown datatype {}!".format(datatype))
        pass
    #
    # make values in rst become a list, so later rst can be used to build a DataFrame
    #
    return rst


def merge_dicts(dic1, dic2):
    for key, value in dic2.items():
        if key not in dic1:
            dic1[key] = value
        else:
            if isinstance(value, list) and isinstance(dic1[key], list):
                dic1[key] += value
            elif isinstance(value, list):
                dic1[key] = value.append(dic1[key])
            elif isinstance(dic1[key], list):
                dic1[key].append(value)
            else:
                dic1[key] = [dic1[key], value]
    return dic1


def parse_wikidata_qualifiers(qualifiers):
    """
        Args:
            qualifiers (dict): Property_ID ==> a list of snaks
        Returns:
            A dict.
    """
    if qualifiers is None:
        return {}
    rst = {}
    for property_id, snaks in qualifiers.items():
        # property = search_entity(property_id, "property", limit=1)[0]['label']
        key_prefix = property_id + ":" + label_desc_dict[property_id][0] + "."
        for snak in snaks:
            datatype = snak.get("datatype")
            datavalue = snak.get("datavalue")
            if datatype is None or datavalue is None:
                continue
            dic = parse_wikidata_datavalue(datavalue, datatype)
            #
            # add prefix to keys
            #
            dic = {key_prefix+k: v for k, v in dic.items()}
            rst = merge_dicts(rst, dic)
    return rst
