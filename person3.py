import kgpl
import plotly.express as px

# the variables ids we use
total_vid = 9
incr_vid = 11

# Get the variable and value
total_var = kgpl.load_var(total_vid)
total_val = kgpl.load_val(total_var.val_id)

incr_var = kgpl.load_var(incr_vid)
incr_val = kgpl.load_val(incr_var.val_id)

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

# process the data for incrment
loc = []
data = []
for (k, v) in incr_val.getConcreteVal().items():
    if k != "AS":
        loc.append(k)
        data.append(v)

# plot
fig = px.choropleth(locations=loc, locationmode="USA-states", color=data, scope="usa")
fig.show()

# generate the ten least cases
L = [(k, v) for (k, v) in incr_val.getConcreteVal().items()]
L.sort(key=lambda x: x[1])
print(L)

least_list = []
for i in range(1, 11):
    least_list.append(L[i])

least_val = kgpl.value(least_list)
least_var = kgpl.variable(least_val.vid)
