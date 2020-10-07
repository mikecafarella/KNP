import kgpl
import plotly.express as px
import plotly

# the variables ids we use
# total_vid = "http://127.0.0.1:5000/var/3"
# prev_vid = "http://127.0.0.1:5000/var/7"

# Get the variable and value
# total_var = kgpl.load_var(total_vid)
# total_val = kgpl.load_val(total_var.val_id)
total_val = kgpl.load_val("http://127.0.0.1:5000/val/5")

# process the data for total cases
loc = []
data = []
for (k, v) in total_val.getConcreteVal().items():
    if k != "AS":
        loc.append(k)
        data.append(v)

# plot
fig = px.choropleth(locations=loc, locationmode="USA-states", color=data, scope="usa")
# fig.show()
fig.write_image("predict_2.png")
pre1 = kgpl.Image("predict_2.png")
kgpl.value(pre1,"predict seconde day image", "Drawer",["http://127.0.0.1:5000/val/5",])

# generate the ten least cases
L = [(k, v) for (k, v) in total_val.getConcreteVal().items()]
L.sort(key=lambda x: x[1])
print(L)

least_list = []
for i in range(1, 11):
    least_list.append(L[i][0])

least_val = kgpl.value(least_list, "least ten states","Drawer",["http://127.0.0.1:5000/val/5",])
# least_var = kgpl.load_var(prev_vid)
# kgpl.set_var(least_var, least_val.getVid(), least_val.comment)
