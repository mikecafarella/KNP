import knps
import plotly.express as px
import plotly

# the variables ids we use
total_vid = knps.server_url + "/var/1"
prev_pic = knps.server_url + "/var/2"
prev_vid = knps.server_url + "/var/3"

# Get the variable and value
total_var = knps.load_var(total_vid)
total_val = knps.load_val(total_var.val_id)

# process the data for total cases
loc = []
data = []
for (k, v) in total_val.getConcreteVal().items():
    if k != "AS":
        loc.append(k)
        data.append(v)

# plot
fig = px.choropleth(locations=loc, locationmode="USA-states",
                    color=data, scope="usa")
# fig.show()
fig.write_image("predict_2.png")
pre1 = knps.File("predict_2.png")
pic = knps.value(pre1, "predict second day image", "Mike", [total_val, ])
# generate the ten least cases
L = [(k, v) for (k, v) in total_val.getConcreteVal().items()]
L.sort(key=lambda x: x[1])
print(L)

least_list = []
for i in range(1, 11):
    least_list.append(L[i][0])

least_val = knps.value(least_list, "least ten states", "Mike", [total_val, ])
least_var = knps.load_var(prev_vid)
prev_pic_val = knps.load_var(prev_pic)
knps.set_var(least_var, least_val.getVid(), least_val.comment)
knps.set_var(prev_pic_val, pic.vid, "New prediction picture")
