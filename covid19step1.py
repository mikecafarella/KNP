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

if __name__ == "__main__":
    r = requests.get("https://api.covidtracking.com/v1/states/daily.json")
    # print(r)
    data_list = r.json()
    # print(data_dict)
    rst = defaultdict(list)
    rst_2 = defaultdict(list)


    twenty_days = datetime.today() - timedelta(days=20)
    before_20 = int (twenty_days.strftime('%Y%m%d'))


    for one_item in data_list:
        file_name = "data/" + str(one_item["date"])
        if one_item["date"] < before_20:
            break
        rst[one_item["state"]].append((one_item["date"], one_item["positive"]))
        rst_2[one_item["date"]].append(
            (one_item["state"], one_item["positive"]))

    # with open("state-(date,positive)", "w")as output_file:
    #     json.dump(rst, output_file)
    #
    # with open("date-(state,positive)", "w") as output_file_2:
    #     json.dump(rst_2, output_file_2)

    myval = kgpl.value(dict(rst))
    kgpl.variable(myval.vid)
        # with open(file_name, "a+") as output_file:
        #     output_file.write(
        #         "(" + one_item["state"] + ", "+str(one_item["positive"]) + ")\n")
