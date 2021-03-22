import knps
import plotly.express as px
import plotly

from lib import get_user_id, create_data_object, get_data_object


USER_NAME = 'Pablo Picasso'
USER_EMAIL = 'pablo@picasso.net'
SOURCE_OBJ_ID = 2

if __name__ == "__main__":
    user_id = get_user_id(USER_EMAIL, USER_NAME)
    data_source = get_data_object(SOURCE_OBJ_ID)

    PREDECESSORS = [data_source['version_id']]

    import json
    print(json.dumps(data_source, indent=2))

    # process the data for total cases
    loc = []
    data = []
    for k, v in data_source['jsondata'].items():
        if k != "AS":
            loc.append(k)
            data.append(v)

    # plot
    fig = px.choropleth(
        locations=loc, locationmode="USA-states", color=data, scope="usa")
    fig.write_image("predict_1.jpg")

    obj_data = create_data_object(
        name = 'COVID Prediction, Next Day, DataViz',
        ownerid = user_id,
        description = "Visualization of COVID prediction data",
        image_file = "predict_1.png",
        comment = "Cloropleth map",
        predecessors = PREDECESSORS
    )

    # pre1 = knps.File("predict_1.png")
    # pic = knps.value(pre1, "Predict 1 image", "Mike", [total_val, ])
    # knps.variable(pic,"picture from Mike")
    #
    # # generate the ten least cases
    # L = [(k, v) for (k, v) in total_val.getConcreteVal().items()]
    # L.sort(key=lambda x: x[1])
    # print(L)
    #
    # least_list = []
    # for i in range(1, 11):
    #     least_list.append(L[i][0])
    #
    # least_val = knps.value(least_list, "Least ten states in the prediction",
    #                        "Mike", [total_val, ])
    # least_var = knps.variable(least_val, "variable holding least ten states")
