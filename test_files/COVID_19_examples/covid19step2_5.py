"""
The knpsVariable should be provided
or its name should be provided corresponding to DATE_TO_PREDICT.
Its value should be updated everytime we run it.
Generate a knpsValue holding a dict.
"""
import requests
import os
import json

from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import numpy as np
from collections import defaultdict

import knps

SERVER_URL = knps.server_url

# PREV_VAR_ID = SERVER_URL + "/var/1"
PREV_VAR_ID = "CovidPrediction"
VAR_ID_GIVEN_BY_USER1 = "LatestCovidData"


def step2_5(_):
    DATE_TO_PREDICT = int(
        (datetime.today() + timedelta(days=1)).strftime('%Y%m%d'))

    # VAR_ID_GIVEN_BY_USER1 = SERVER_URL + "/var/0"

    TRAIN_LENGTH = 20

    date = datetime.strptime(str(DATE_TO_PREDICT), '%Y%m%d')
    starting_date = date - timedelta(days=TRAIN_LENGTH)
    start = starting_date.strftime('%Y%m%d')
    temp_dict = {}

    # needed_var_id = knps.load_var(VAR_ID_GIVEN_BY_USER1)
    # val_knps = knps.load_val(needed_var_id.val_id)
    # data_source = val_knps.val
    data_source = knps.get_var_content(VAR_ID_GIVEN_BY_USER1)

    for key, val in data_source.items():
        temp_list = []
        i = 1
        for one_day in val:
            if one_day[0] < DATE_TO_PREDICT and one_day[0] >= int(start):
                temp_list.append([i, one_day[1]])
                i += 1
        temp_dict[key] = temp_list

    rst = {}
    for key, val in temp_dict.items():
        X = []
        Y = []
        for one_day_val in val:
            X.append(one_day_val[0])
            Y.append(one_day_val[1])

        X = np.array(X).reshape((-1, 1))

        model = LinearRegression()
        model.fit(X, Y)
        X_predict = np.array([0, ]).reshape(
            (-1, 1))  # put the dates of which you want to predict kwh here
        y_predict = model.predict(X_predict)
        rst[key] = int(round(y_predict[0].item()))

    var_comment = "Prediction for COVID-19 cumulative positive \
        cases for all states in the US in the next day"
    val_comment = "Prediction for COVID-19 cumulative positive \
        cases for all states in the US for " + \
        (datetime.today() + timedelta(days=1)).strftime('%Y%m%d')

    knps.publish_update(rst, val_comment, PREV_VAR_ID,
                        "Betty", [VAR_ID_GIVEN_BY_USER1, ])
    # myval = knps.create_value(rst, val_comment, "Betty", [VAR_ID_GIVEN_BY_USER1, ])
    # myval.update_label(PREV_VAR_ID, var_comment)
    # prev_var = knps.load_var(PREV_VAR_ID)
    # knps.set_var(prev_var, myval.vid, var_comment)


if __name__ == "__main__":
    step2_5(1)
