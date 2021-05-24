import plotly.express as px
import plotly

from lib import get_user_id, create_data_object, get_data_object

USER_NAME = 'Jenny Vo-Phamhi'
USER_EMAIL = 'jennyvo@umich.edu'

# Load the ID for the source we're using from our makeshift local store
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
        image_file = "predict_1.jpg",
        comment = "Cloropleth map",
        predecessors = PREDECESSORS
    )

    data_obj_id = obj_data['id']
    version_id = obj_data['versions'][0]['id']

    # Save the ID for the data object locally, for use in the next step
    with open("step_3_obj_id.txt", "wt") as f:
        f.write(str(data_obj_id))
