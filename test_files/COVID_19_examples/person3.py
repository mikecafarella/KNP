import knps
import plotly.express as px
import plotly

VAR_FROM_BETTY = "Prediction"

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
    #     locations=loc, locationmode="USA-states", color=data, scope="usa")
    # fig.write_image("predict_1.png")
    pre1 = knps.File("predict_1.png")
    pic = knps.create_value(pre1, "Predict 1 image", "Charlie", [VAR_FROM_BETTY, ])
    pic.create_label("PredictionPic","picture from Charlie")

    # generate the ten least cases
    L = [(k, v) for (k, v) in total_val.items()]
    L.sort(key=lambda x: x[1])
    print(L)

    least_list = []
    for i in range(1, 11):
        least_list.append(L[i][0])

    least_val = knps.create_value(least_list, "Least ten states in the prediction",
                           "Charlie", [VAR_FROM_BETTY, ])
    least_val.create_label("LeastTen", "variable holding least ten states")
