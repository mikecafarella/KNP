import kgpl_client as kgpl
import plotly.express as px
import plotly

# the variables ids we use
# total_vid = "http://127.0.0.1:5000/var/1"
# prev_vid = "http://127.0.0.1:5000/var/2"
# prev_pic =  "http://127.0.0.1:5000/var/3"
total_vid = "http://lasagna.eecs.umich.edu:8000/var/1"
prev_vid = "http://lasagna.eecs.umich.edu:8000/var/2"
prev_pic =  "http://lasagna.eecs.umich.edu:8000/var/3"

# Get the variable and value
total_var = kgpl.load_var(total_vid)
total_val = kgpl.load_val(total_var.val_id)
# total_val = kgpl.load_val("http://127.0.0.1:5000/val/5")

# process the data for total cases
loc = []
data = []
for (k, v) in total_val.getConcreteVal().items():
    if k != "AS":
        loc.append(k)
        data.append(v)

# plot
fig = px.choropleth(locations=loc, locationmode="USA-states", color=data, scope="usa")
fig.show()
fig.write_image("predict_2.png")
pre1 = kgpl.File("predict_2.png")
pic = kgpl.value(pre1,"predict second day image", "Drawer",[total_val,])
# generate the ten least cases
L = [(k, v) for (k, v) in total_val.getConcreteVal().items()]
L.sort(key=lambda x: x[1])
print(L)

least_list = []
for i in range(1, 11):
    least_list.append(L[i][0])

least_val = kgpl.value(least_list, "least ten states","Drawer",[total_val,])
least_var = kgpl.load_var(prev_vid)
prev_pic_val = kgpl.load_var(prev_pic)
kgpl.set_var(least_var, least_val.getVid(), least_val.comment)
kgpl.set_var(prev_pic_val,pic.vid,"New prediction picture")