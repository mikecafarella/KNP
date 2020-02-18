import pandas as pd
import flexmatcher
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import seaborn as sns

def pd_to_str(df):
    df.is_copy = False
    for column in df.columns:
        df.loc[:, column] = df.loc[:, column].apply(str)
    return df

# https://python-graph-gallery.com/30-basic-boxplot-with-seaborn/
train_data_1 = sns.load_dataset('iris')
# print(pd.DataFrame(train_data_1.columns))
train_data_1 = pd_to_str(train_data_1[["species", "sepal_length"]])
# assert(0)
mapping_1 = {"species": "x", "sepal_length": "y"}


# https://seaborn.pydata.org/generated/seaborn.boxplot.html
train_data_2 = sns.load_dataset("tips")
train_data_2 = pd_to_str(train_data_2[["day", "total_bill"]])
mapping_2 = {"day": "x", "total_bill": "y"}


# https://www.programcreek.com/python/example/96223/seaborn.boxplot
data = {"group_by": [None], "column": [None]}
train_data_3 = pd.DataFrame(data=data)
mapping_3 = {"group_by": "x", "column": "y"}


#https://cmdlinetips.com/2018/03/how-to-make-boxplots-in-python-with-pandas-and-seaborn/
train_data_4 = pd.DataFrame({"continent":[None], "lifeExp":[None]})
mapping_4 = {"continent": "x", "lifeExp": "y"}


# https://www.sharpsightlabs.com/blog/seaborn-boxplot/
train_data_5 = pd.DataFrame({"score":[None], "class":[None]})
mapping_5 = {"score": "x", "class": "y"}

# synthetic data
train_data_6 = pd.DataFrame({"year":["2018"], "population":["100k"]})# "not relevant":["not"]})
mapping_6 = {"year": "x", "population": "y"}

schema_list = [train_data_1, train_data_2, train_data_3, train_data_4, train_data_5, train_data_6]
mapping_list = [mapping_1, mapping_2, mapping_3, mapping_4, mapping_5, mapping_6]
fm = flexmatcher.FlexMatcher(schema_list, mapping_list)
# print(type(fm.train_data))
fm.train()
# print(fm.prediction_list[0][0])
new_data = {
    "amount": ["1", "2", "3", "4"],
    "country": ["China", "China", "USA", "USA"]
}
new_data = pd.DataFrame(data=new_data)
predicted_mapping = fm.make_prediction(new_data)

print(predicted_mapping)