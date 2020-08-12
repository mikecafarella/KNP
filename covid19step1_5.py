"""
Get the data from covidtracking.com.
Store it in a KGPLValue.
Assign to a KGPLVariable.
Everytime we run this, the KGPLVariable is not changed.
But the KGPLValue it points to should be updated.
i.e. a new KGPLValue is created.
"""
import kgpl
import requests
import json
from collections import defaultdict
from datetime import datetime, timedelta

PREV_VAR_ID = 1

def step1_5(_):

    today = datetime.today() - timedelta(days=1)
    twenty_days = today - timedelta(days=20)
    before_20 = int(twenty_days.strftime('%Y%m%d'))
    today = int(today.strftime('%Y%m%d'))

    r = requests.get("https://api.covidtracking.com/v1/states/daily.json")
    # print(r)
    data_list = r.json()
    # print(data_dict)
    rst = defaultdict(list)
    rst_2 = defaultdict(list)

    for one_item in data_list:
        file_name = "data/" + str(one_item["date"])
        if one_item["date"] > today:
            continue
        if one_item["date"] < before_20:
            break
        rst[one_item["state"]].append((one_item["date"], one_item["positive"]))
        rst_2[one_item["date"]].append(
            (one_item["state"], one_item["positive"]))

    myval = kgpl.value(dict(rst))

    prev_var = kgpl.load_var(PREV_VAR_ID)
    kgpl.set_var(prev_var, myval.vid)


if __name__ == "__main__":
    step1_5(1)