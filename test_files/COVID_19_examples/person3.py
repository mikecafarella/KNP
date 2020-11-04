import knps
import plotly.express as px
import plotly

if __name__ == "__main__":
    total_vid = "http://lasagna.eecs.umich.edu:8000/var/1"
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
    fig = px.choropleth(
        locations=loc, locationmode="USA-states", color=data, scope="usa")
    fig.write_image("predict_1.png")
    pre1 = knps.File("predict_1.png")
    pic = knps.value(pre1, "Predict 1 image", "Mike", [total_val, ])
    knps.variable(pic,"picture from Mike")

    # generate the ten least cases
    L = [(k, v) for (k, v) in total_val.getConcreteVal().items()]
    L.sort(key=lambda x: x[1])
    print(L)

    least_list = []
    for i in range(1, 11):
        least_list.append(L[i][0])

    least_val = knps.value(least_list, "Least ten states in the prediction",
                           "Mike", [total_val, ])
    least_var = knps.variable(least_val, "variable holding least ten states")
   