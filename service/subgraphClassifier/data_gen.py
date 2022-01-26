# this file creates the data needed for the classifier
import pandas as pd
import json 
import random
import matplotlib.pyplot as plt
import numpy as np
import shutil


DATA_DIR = 'data/'

def get_csv_name(csv_path):
    return csv_path.split('/')[-1].split('.')[0]

def change_title(csv_path):
    changed_title = '{}_titleChange.csv'.format(get_csv_name(csv_path))
    shutil.copy(csv_path, changed_title)

def drop_column(csv_path):
    df = pd.read_csv(csv_path)
    cols = [col for col in df.columns if "Unnamed" not in col]
    col = 'test3'
    while col == 'test3':
        col = random.choice(cols)
    del df[col]
    cols = df.columns
    df = df.rename(lambda x: x if "Unnamed" not in x else "", axis='columns')
    df.to_csv('{}_dropCol.csv'.format(get_csv_name(csv_path)), index=False)

def make_viz(csv_path):
    df = pd.read_csv(csv_path)
    cols = df.columns
    x_cols = []
    y_cols = []
    for col in cols[1:]:
         if np.issubdtype(df[col].dtype, np.number):
            x_cols.append(col)
            if 'date' not in col and 'realtime' not in col:
                y_cols.append(col)
    x_col = y_col = None
    while (x_col == y_col):
        x_col = random.choice(x_cols)
        y_col = random.choice(y_cols)
    x_s = [i for i in df[x_col]]
    y_s = [i for i in df[y_col]]
    plt.plot(x_s, y_s)
    plt.draw()
    plt.savefig('{}_viz.png'.format(get_csv_name(csv_path)))
  

if __name__ == "__main__":
    drop_column('Book1.csv')
    # make_viz('Book1.csv')
    # change_title('Book1.csv')
    pass
