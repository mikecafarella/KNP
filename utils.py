import ast
import pandas as pd
import itertools
import more_itertools
import random
import inspect
import methods
import glob
import matplotlib.pyplot as plt
import json
import yaml

def parse(source):
    """return Operator_string, """
    call = ast.parse(source, "operator string", mode="eval").body
    print(ast.dump(call))
    # TODO: data is not handled 
    return call.func.id, [arg.value for arg in call.args[1:]], [(keyword.arg, keyword.value.value) for keyword in call.keywords]


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
        
        if test_one_mapping(method, actual_mapping, criterion):
            count_ok_mappings += 1
            if output_path:
                with open(output_path, 'a') as f:
                    yaml.dump((index, mapping), f)
                    f.write("\n")
            else:
                print(index, mapping)
            # break
        count_total_mappings = 0
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
            test_mappings(method, df, output_path="{}/{}_runnable_mappings.yml".format(output_path, dataset_name))
        else:
            test_mappings(method, df)


def run_mappings_from_file():
    pass


test_mappings_for_seaborn(methods.OneNumericSeveralGroupBoxPlot, output_path="outputs")

iris = load_seaborn_dataset('iris')