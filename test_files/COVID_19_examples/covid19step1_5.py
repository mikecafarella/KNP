"""
Get the data from covidtracking.com.
Store it in a knpsValue.
Assign to a knpsVariable.
Everytime we run this, the knpsVariable is not changed.
But the knpsValue it points to should be updated.
i.e. a new knpsValue is created.
"""
import knps
import requests
import json
from collections import defaultdict
from datetime import datetime, timedelta

# PREV_VAR_ID = knps.server_url + "/var/0"
PREV_VAR_ID = "LatestCovidData"

def step1_5(_):

    today = datetime.today() - timedelta(days=3)
    twenty_days = today - timedelta(days=20)
    before_20 = int(twenty_days.strftime('%Y%m%d'))
    today = int(today.strftime('%Y%m%d'))

    r = requests.get("https://api.covidtracking.com/v1/states/daily.json")
    data_list = r.json()
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

    val_comment = "The COVID-19 cumulative positive cases for all states\
         in the US from " + str(before_20) + " to " + str(today)
    var_comment = "The COVID-19 cumulative positive cases for all states\
         in the US in the last 20 days"
    myval = knps.create_value(dict(rst), val_comment, "Alice")
    myval.update_label(PREV_VAR_ID,var_comment)
    # try:
    #     prev_var = knps.load_var(PREV_VAR_ID)  # Enabled in the later days
    #     knps.set_var(prev_var, myval.vid, var_comment)
    # except:
    #     print('except')




if __name__ == "__main__":
    step1_5(1)
