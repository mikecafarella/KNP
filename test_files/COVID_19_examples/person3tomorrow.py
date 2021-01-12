import knps
import plotly.express as px
import plotly

# the variables ids we use
# total_vid = knps.server_url + "/var/1"
# prev_pic = knps.server_url + "/var/2"
# prev_vid = knps.server_url + "/var/3"
TOTAL_VID = "CovidPrediction"
PREV_PIC = "CovidPredictionPic"
PREV_VID = "TenStatesWithFewestCovid"

# Get the variable and value
# total_var = knps.load_var(total_vid)
# total_val = knps.load_val(total_var.val_id)
total_val = knps.get_var_content(TOTAL_VID)

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
                    PREV_PIC, "Charlie", [TOTAL_VID, ])
# pic = knps.create_value(pre1, "predict second day image",
#                         "Charlie", [total_vid, ])
# pic.update_label(prev_pic, "New prediction picture")
# generate the ten least cases
L = [(k, v) for (k, v) in total_val.items()]
L.sort(key=lambda x: x[1])
# print(L)

least_list = []
for i in range(1, 11):
    least_list.append(L[i][0])
knps.publish_update(least_list, "Ten states with the fewest COVID cases",
                    PREV_VID, "Charlie", [TOTAL_VID, ])
# least_val = knps.create_value(
#     least_list, "least ten states", "Charlie", [TOTAL_VID, ])
# least_val.update_label(PREV_VID, "least ten states updated")
# least_var = knps.load_var(prev_vid)
# knps.set_var(least_var, least_val.getVid(), least_val.comment)

# prev_pic_val = knps.load_var(prev_pic)
# knps.set_var(prev_pic_val, pic.vid, )
