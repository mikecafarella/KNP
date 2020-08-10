"""
The KGPLVariable should be provided
or its name should be provided corresponding to DATE_TO_PREDICT.
Its value should be updated everytime we run it.
Generate a KGPLValue holding a dict.
"""
import requests
import os
import json

from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import numpy as np
from collections import defaultdict

import kgpl


# For a fair prediction, put a value between $today to 20200715.


# It ends one day earlier.
def step2(_):
    DATE_TO_PREDICT = int(
        (datetime.today() + timedelta(days=1)).strftime('%Y%m%d'))
    # print(DATE_TO_PREDICT)
    # DATE_TO_PREDICT = 20200601
    VAR_ID_GIVEN_BY_USER1 = 1
    TRAIN_LENGTH = 20

    date = datetime.strptime(str(DATE_TO_PREDICT), '%Y%m%d')
    starting_date = date - timedelta(days=TRAIN_LENGTH)
    start = starting_date.strftime('%Y%m%d')
    temp_dict = {}

    needed_var_id = kgpl.load_var(VAR_ID_GIVEN_BY_USER1)
    val_kgpl = kgpl.load_val(needed_var_id.val_id)
    data_source = val_kgpl.val
    # print(data_source)

    for key, val in data_source.items():
        temp_list = []
        i = 1
        for one_day in val:
            if one_day[0] < DATE_TO_PREDICT and one_day[0] >= int(start):
                temp_list.append([i, one_day[1]])
                i += 1
        temp_dict[key] = temp_list

    # print(temp_dict)
    rst = {}
    for key, val in temp_dict.items():
        X = []
        Y = []
        for one_day_val in val:
            X.append(one_day_val[0])
            Y.append(one_day_val[1])
        # print(X)
        # print(Y)
        X = np.array(X).reshape((-1, 1))
        # print(X)
        # print(Y)
        model = LinearRegression()
        model.fit(X, Y)
        # print('coefficient of determination:',  model.score(X, y))
        X_predict = np.array([0, ]).reshape(
            (-1, 1))  # put the dates of which you want to predict kwh here
        y_predict = model.predict(X_predict)
        rst[key] = int(round(y_predict[0].item()))
    # print(rst)
    # do prediction
    myval = kgpl.value(rst).vid
    print( "Below is the variable containing a dict "
          "with the prediction of all states for tomorrow: ")
    kgpl.variable(myval)


if __name__ == "__main__":
    step2(1)

    # with open("rst", "w") as output_file:
    #     json.dump(rst, output_file)
    # d=datetime.today().strftime('%Y%m%d')
    # print(d)
    # file name can be decreasing.
    # KGPLVariable can also be decreasing.
    # data_date = datetime.today() - timedelta(days=3) # Since the data is not 100% up to date

    # path = os.walk("data")
    # for root, directories, files in path:
    #     for file in files:
    #         file_date = int(file)
    #         if file_date < DATE_TO_PREDICT and file_date >= int(start):
    #             with open("data/"+file, "r") as input_file:
    #                 for line in input_file:
    #                     print(line)
    #                     tuple_val = json.loads(line.strip())
    #                     data_source[tuple_val[0]].append(tuple_val[1])

    # print(data_source)

    #     # X = np.array([[1, 2], [1, 2], [2, 4], [2, 4]]).reshape((-1, 1))
    #     X = np.array([1,2,3]).reshape((-1,1))  # put your dates in here
    #     y = [2,4,6]  # put your kwh in here
    #     # y = 2
    #     model = LinearRegression()
    #     model.fit(X, y)
    #     print('coefficient of determination:',  model.score(X, y))
    #     X_predict =np.array([5, 20]).reshape((-1,1)) # put the dates of which you want to predict kwh here
    #     y_predict = model.predict(X_predict)
    #     print(y_predict)
    #     for one_item  in y_predict:
    #         print(one_item.item())
    #         print(type(one_item.item()))
    #         print(int(round(one_item.item())))
    # # Assume the user will enter a valid date
    # # i.e. before the latest data can provide
    # # and after 20200714
    #
