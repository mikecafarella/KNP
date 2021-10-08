import knps
import plotly.express as px
import plotly

# the variables ids we use
LABEL_FROM_BETTY = "CovidPrediction"
PREV_PIC = "CovidPredictionPic"
PREV_VID = "TenStatesWithFewestCovid"

# Get the variable and value
total_val = knps.get_label_content(LABEL_FROM_BETTY)

# process the data for total cases
loc = []
data = []
for (k, v) in total_val.items():
    if k != "AS":
        loc.append(k)
        data.append(v)

# plot
# fig = px.choropleth(locations=loc, locationmode="USA-states",
                    # color=data, scope="usa")
# fig.show()
# fig.write_image("predict_2.png")
pre1 = knps.File("predict_2.png")
knps.publish_update(pre1, "Second week prediction image",
                    PREV_PIC, "Charlie", [LABEL_FROM_BETTY, ])
# generate the ten least cases
L = [(k, v) for (k, v) in total_val.items()]
L.sort(key=lambda x: x[1])
# print(L)

least_list = []
for i in range(1, 11):
    least_list.append(L[i][0])
knps.publish_update(least_list, "Ten states with the fewest COVID cases",
                    PREV_VID, "Charlie", [LABEL_FROM_BETTY, ])
