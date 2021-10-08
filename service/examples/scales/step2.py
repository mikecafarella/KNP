"""
Get the data from covidtracking.com.
Store it in a knpsValue.
Assign to a knpsVariable.
Everytime we run this, the knpsVariable is not changed.
But the knpsValue it points to should be updated.
i.e. a new knpsValue is created.
"""
import requests
import json
from collections import defaultdict
from datetime import datetime, timedelta
from urllib.request import urlopen

from lib import get_user_id, create_data_object, update_data_object

USER_NAME = "Mike Anderson"
USER_EMAIL = "mrander@umich.edu"

sample_data_file = "data/Unemployment_data_2019.csv"
sample_data_file2 = "data/all_court_records.csv"
sample_data_file3 = "data/judicial_districts.csv"
sample_data_file4 = "data/fips_counties.csv"

if __name__ == "__main__":
    user_id = get_user_id(USER_EMAIL, USER_NAME)
    user_id2 = get_user_id("andrewpaley2022@u.northwestern.edu", "Andrew Paley")
    user_id3 = get_user_id("alicezou@umich.edu", "Jiayun Zou")
    user_id4 = get_user_id("michjc@csail.mit.edu", "Michael Cafarella")
    user_id5 = get_user_id("ctm310@yahoo.com", "Carol McLaughlin")

    map_func = """def cloropleth_fips_map(dobj_id, columns=[]):
    # Parameters: (fips_column_name, data_column_name)
    from urllib.request import urlopen
    import json
    import plotly.graph_objects as go
    import pandas as pd
    from io import BytesIO, StringIO

    GEO_DATA_ID = 25
    counties = get_dobj_contents(GEO_DATA_ID)

    input_data = get_dobj_contents(dobj_id)

    df = pd.read_csv(StringIO(input_data.decode('utf-8')), dtype={columns[0]: str})

    fig = go.Figure(go.Choroplethmapbox(geojson=counties, locations=df[columns[0]], z=df[columns[1]],
                                      colorscale="Viridis", zmin=min(df[columns[1]]), zmax=max(df[columns[1]]),
                                      marker_opacity=0.5, marker_line_width=0))
    fig.update_layout(mapbox_style="carto-positron",
                    mapbox_zoom=5.6, mapbox_center = {"lat": 43.15, "lon": -76.14})
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    #{"lat": 37.0902, "lon": -95.7129}
    output_buffer = BytesIO()
    fig.write_image(output_buffer, format='png')
    output = output_buffer.getvalue()

    return {'contents': output, 'datatype': '/datatypes/img', 'mimetype': 'image/png', 'predecessors': [GEO_DATA_ID]}"""

    code_obj_data = update_data_object(
        objectid = 30,
        ownerid = user_id,
        code = map_func,
        comment = 'Inputs: (dobj_id, [fips_col_name, data_col_name])'
    )
