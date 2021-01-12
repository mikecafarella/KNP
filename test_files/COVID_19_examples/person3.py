import knps
import plotly.express as px
import plotly

VAR_FROM_BETTY = "CovidPrediction"

if __name__ == "__main__":
    # total_vid = knps.server_url + "/var/1"
    # total_var = knps.load_var(total_vid)
    # total_val = knps.load_val(total_var.val_id)
    total_val = knps.get_var_content(VAR_FROM_BETTY)
    # process the data for total cases
    loc = []
    data = []
    for (k, v) in total_val.items():
        if k != "AS":
            loc.append(k)
            data.append(v)

    # plot
    # fig = px.choropleth(
        # locations=loc, locationmode="USA-states", color=data, scope="usa")
    # fig.write_image("predict_1.png")
    pre1 = knps.File("predict_1.png")
    knps.publish_new(pre1, "Predict image for week one",
                     "CovidPredictionPic", "Charlie", [VAR_FROM_BETTY, ])

    # generate the ten least cases
    L = [(k, v) for (k, v) in total_val.items()]
    L.sort(key=lambda x: x[1])
    print(L)

    least_list = []
    for i in range(1, 11):
        least_list.append(L[i][0])

    knps.publish_new(least_list, "Ten states with the fewest COVID cases",
                     "TenStatesWithFewestCovid", "Charlie", [VAR_FROM_BETTY, ])
    # least_val = knps.create_value(least_list, "Least ten states in the prediction",
    #   "Charlie", [VAR_FROM_BETTY, ])
    # least_val.create_label("LeastTen", "variable holding least ten states")
