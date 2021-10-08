"""
The knpsVariable should be provided
or its name should be provided corresponding to DATE_TO_PREDICT.
Its value should be updated everytime we run it.
Generate a knpsValue holding a dict.
"""
import requests
import os
import json

from datetime import datetime, timedelta, date
from sklearn.linear_model import LinearRegression
import numpy as np
from collections import defaultdict

from lib import get_user_id, create_data_object, get_data_object


USER_NAME = 'Yuze Lou'
USER_EMAIL = 'yuze@example.com'

# Load the ID for the source we're using from our makeshift local store
with open("step_1_obj_id.txt", "rt") as f:
    for line in f:
        SOURCE_OBJ_ID = int(line.strip())

print("Using Data Object ID: ", SOURCE_OBJ_ID)

# It ends one day earlier.
def step2(_):
    user_id = get_user_id(USER_EMAIL, USER_NAME)
    data_source = get_data_object(SOURCE_OBJ_ID)

    PREDECESSORS = [data_source['version_id']]


    DATE_TO_PREDICT = int(
        (date.fromisoformat('2020-12-28')).strftime('%Y%m%d'))
    TRAIN_LENGTH = 20

    starting_date = datetime.strptime(str(DATE_TO_PREDICT), '%Y%m%d') - timedelta(days=TRAIN_LENGTH)
    start = starting_date.strftime('%Y%m%d')
    temp_dict = {}

    for key, val in data_source['jsondata'].items():
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

    val_comment = "Prediction for COVID-19 cumulative positive cases for all states in the US for " + str(DATE_TO_PREDICT)
    var_comment = "Prediction for COVID-19 cumulative positive cases for all states in the US in the next day"

    obj_data = create_data_object(
        name = 'COVID Prediction, Next Day',
        ownerid = user_id,
        description = var_comment,
        jsondata = dict(rst),
        comment = val_comment,
        predecessors = PREDECESSORS
    )

    data_obj_id = obj_data['id']
    version_id = obj_data['versions'][0]['id']

    # Save the ID for the data object locally, for use in the next step
    with open("step_2_obj_id.txt", "wt") as f:
        f.write(str(data_obj_id))


if __name__ == "__main__":
    step2(1)
