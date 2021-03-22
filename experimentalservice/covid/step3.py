import knps
import plotly.express as px
import plotly

from lib import get_user_id, create_data_object, get_data_object


USER_NAME = 'Jenny Vo-Phamhi'
USER_EMAIL = 'jennyvo@umich.edu'

with open("step_2_obj_id.txt", "rt") as f:
    for line in f:
        SOURCE_OBJ_ID = int(line.strip())

print("Using Data Object ID: ", SOURCE_OBJ_ID)

if __name__ == "__main__":
    user_id = get_user_id(USER_EMAIL, USER_NAME)
    data_source = get_data_object(SOURCE_OBJ_ID)

    PREDECESSORS = [data_source['version_id']]

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
