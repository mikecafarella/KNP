import kgpl
import plotly.express as px
import plotly

if __name__ == "__main__":
    # the variables ids we use
    # total_vid = "http://127.0.0.1:5000/var/1"
    total_vid = "http://lasagna.eecs.umich.edu:5000/var/1"

    # Get the variable and value
    total_var = kgpl.load_var(total_vid)
    # total_val = total_var.getConcreteVal()
    total_val = kgpl.load_val(total_var.val_id)
    # total_val = kgpl.load_val("http://127.0.0.1:5000/val/1")

    # process the data for total cases
    loc = []
    data = []
    for (k, v) in total_val.getConcreteVal().items():
        if k != "AS":
            loc.append(k)
            data.append(v)

    # plot
    # fig = px.choropleth(
    #     locations=loc, locationmode="USA-states", color=data, scope="usa")
    # fig.write_image("predict_1.png")
    pre1 = kgpl.Image("predict_1.png")
    pic = kgpl.value(pre1, "Predict 1 image", "Drawer", [total_val, ])
    kgpl.variable(pic,"picture from drawer")
    # fig.show()

    # generate the ten least cases
    L = [(k, v) for (k, v) in total_val.getConcreteVal().items()]
    L.sort(key=lambda x: x[1])
    print(L)

    least_list = []
    for i in range(1, 11):
        least_list.append(L[i][0])

    least_val = kgpl.value(least_list, "Least ten states in the prediction",
                           "Drawer", [total_val, ])
    least_var = kgpl.variable(least_val, "variable holding least ten states")
   