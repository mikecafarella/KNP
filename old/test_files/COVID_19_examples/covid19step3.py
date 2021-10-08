import knps
import plotly.express as px
import plotly

LABEL_FROM_BETTY = "CovidPrediction"

if __name__ == "__main__":
    total_val = knps.get_label_content(LABEL_FROM_BETTY)
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
        "CovidPredictionPic", "Charlie", 
        [LABEL_FROM_BETTY, ])

    # generate the ten least cases
    L = [(k, v) for (k, v) in total_val.items()]
    L.sort(key=lambda x: x[1])
    print(L)

    least_list = []
    for i in range(1, 11):
        least_list.append(L[i][0])

    knps.publish_new(least_list,
        "Ten states with the fewest COVID cases",
        "TenStatesWithFewestCovid", 
        "Charlie", [LABEL_FROM_BETTY, ])
