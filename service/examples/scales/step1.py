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

    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
      counties = json.load(response)

    json_obj_data = create_data_object(
        name = 'GeoJSON US County FIPS data',
        ownerid = user_id,
        description = 'Geo FIPS data for US Counties',
        data = counties,
        comment = 'Downloaded from Plotly',
        datatype = '/datatypes/json',
        mimetype = 'application/json'
    )


    csv_obj_data = create_data_object(
        name = '2019 U.S. Unemployment and Income Data',
        ownerid = user_id,
        description = 'Unemployment and income data by county',
        datafile = sample_data_file,
        comment = 'Downloaded from USDA',
        datatype = '/datatypes/csv',
        mimetype = 'text/csv'
    )

    csv_obj_data = create_data_object(
        name = '2016 Court Cases - All Districts',
        ownerid = user_id2,
        description = 'Court cases by district',
        datafile = sample_data_file2,
        comment = 'Downloaded from Scales',
        datatype = '/datatypes/csv',
        mimetype = 'text/csv'
    )

    csv_obj_data = create_data_object(
        name = 'U.S. Judicial Districts by County',
        ownerid = user_id2,
        description = 'US counts annotated by Judicial District',
        datafile = sample_data_file3,
        comment = 'From the web',
        datatype = '/datatypes/csv',
        mimetype = 'text/csv'
    )

    csv_obj_data = create_data_object(
        name = 'FIPS Codes for US Counties',
        ownerid = user_id4,
        description = 'FIPS Codes for US Counties',
        datafile = sample_data_file4,
        comment = 'Downloaded from bls.gov',
        datatype = '/datatypes/csv',
        mimetype = 'text/csv'
    )

    map_func = """def cloropleth_county_map(dobj_id, columns=[]):
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

    code_obj_data = create_data_object(
        name = 'US County Chloropleth Map Function',
        ownerid = user_id,
        description = 'Function to create Chloropleth Maps from US County Data',
        code = map_func,
        comment = 'Inputs: (dobj_id, [fips_col_name, data_col_name])'
    )



    fips_func = """def add_fips_codes_counties(dobj_id, params=[]):
    # params = (county column, state column)
    from io import StringIO
    import csv

    FIPS_DATA = 29
    fips_csv = StringIO(get_dobj_contents(FIPS_DATA).decode())

    fips = {}
    fips_header = {}
    reader = csv.reader(fips_csv, delimiter=',', quotechar='"')
    for row in reader:
        if len(fips_header) == 0:
            fips_header = {x: i for i, x in enumerate(row)}
        else:
            fips[row[fips_header['area_name']]] = row[fips_header['fips_txt']]


    input_data = get_dobj_contents(dobj_id)
    csv_file = StringIO(input_data.decode())

    reader = csv.reader(csv_file, delimiter=',', quotechar='"')

    output = []
    header = {}
    out_str = StringIO()
    writer = csv.writer(out_str, delimiter=',', quotechar='"')

    for row in reader:
        if len(header) == 0:
            writer.writerow(row + ['fips_code'])
            header = {x: i for i, x in enumerate(row)}
        else:
            county = row[header[params[0]]]
            state = row[header[params[1]]]
            if state.lower() in ABBREV_US_STATE:
                state = ABBREV_US_STATE[state.lower()]
            fips_code = fips["{}, {}".format(county, state)]
            writer.writerow(row + [fips_code])

    return {'contents': out_str.getvalue().encode(), 'datatype': '/datatypes/csv', 'mimetype': 'text/csv', 'predecessors': [FIPS_DATA]}"""

    code_obj_data = create_data_object(
        name = 'Add FIPS',
        ownerid = user_id3,
        description = 'Adds additional FIPS column to CSV containing US county column',
        code = fips_func,
        comment = 'Inputs: (dobj_id, [county_col_name, state_col_name])'
    )


    filter_func = """def filter_csv_by_text(dobj_id, params=[]):
    # params = (column to filter, string to match)
    from io import StringIO
    import csv

    input_data = get_dobj_contents(dobj_id)
    csv_file = StringIO(input_data.decode())

    reader = csv.reader(csv_file, delimiter=',', quotechar='"')

    output = []
    header = {}
    out_str = StringIO()
    writer = csv.writer(out_str, delimiter=',', quotechar='"')

    for row in reader:
        if len(header) == 0:
            writer.writerow(row)
            header = {x: i for i, x in enumerate(row)}
        else:
            if params[1] in row[header[params[0]]]:
                writer.writerow(row)

    return {'contents': out_str.getvalue().encode(), 'datatype': '/datatypes/csv', 'mimetype': 'text/csv', 'predecessors': []}"""

    code_obj_data = create_data_object(
        name = 'Filter CSV by text value',
        ownerid = user_id4,
        description = 'Function to filter CSV by text value in one column',
        code = filter_func,
        comment = 'Inputs: (dobj_id, [col_name, filter_text])'
    )

    filter_func = """def aggregate_csv_mean(dobj_id, params=[]):
    # params = (group by column, aggegrate column)
    from io import StringIO
    import csv

    input_data = get_dobj_contents(dobj_id)
    csv_file = StringIO(input_data.decode())

    reader = csv.reader(csv_file, delimiter=',', quotechar='"')

    header = {}
    vals = {}

    for row in reader:
        if len(header) == 0:
            header = {x: i for i, x in enumerate(row)}
        else:

            if row[header[params[0]]] not in vals:
                vals[row[header[params[0]]]] = []
            try:
                vals[row[header[params[0]]]].append(float(row[header[params[1]]]))
            except:
                pass

    out_str = StringIO()
    writer = csv.writer(out_str, delimiter=',', quotechar='"')
    writer.writerow([params[0], params[1]])
    for k, v in vals.items():
        writer.writerow([k, sum(v)/len(v)])

    return {'contents': out_str.getvalue().encode(), 'datatype': '/datatypes/csv', 'mimetype': 'text/csv', 'predecessors': []}"""

    code_obj_data = create_data_object(
        name = 'Mean of CSV column, group by',
        ownerid = user_id,
        description = 'Function to find mean of CSV column, grouped by another column',
        code = filter_func,
        comment = 'Inputs: (dobj_id, [group by column, aggregate column])'
    )

    filter_func = """def join_csvs(dobj_id, params=[]):
    # params = (join csv, join column1, join column2, filter_col, filter_val)
    from io import StringIO
    import csv
    import json

    input_data = get_dobj_contents(dobj_id)
    csv_file = StringIO(input_data.decode())

    join_data = get_dobj_contents(params[0])
    join_file = StringIO(join_data.decode())

    reader = csv.reader(csv_file, delimiter=',', quotechar='"')

    header = {}
    table1 = {}

    output_header = []

    for row in reader:
        if len(header) == 0:
            header = {x: i for i, x in enumerate(row)}
            output_header += row
        else:
            join_idx = header[params[1]]
            if row[join_idx] not in table1:
                table1[row[join_idx]] = []
            table1[row[join_idx]].append(row)

    reader = csv.reader(join_file, delimiter=',', quotechar='"')

    out_str = StringIO()
    writer = csv.writer(out_str, delimiter=',', quotechar='"')

    join_header = {}
    for row in reader:
        if len(join_header) == 0:
            join_header = {x: i for i, x in enumerate(row)}
            output_header += row[:join_header[params[2]]]
            output_header += row[join_header[params[2]]+1:]
            writer.writerow(output_header)
        else:
            if params[3] in join_header and row[join_header[params[3]]] != params[4]:
                continue
            join_idx = join_header[params[2]]
            if row[join_idx] in table1:
                for t1 in table1[row[join_idx]]:
                    out_data = []
                    out_data += t1
                    out_data += row[:join_idx]
                    out_data += row[join_idx+1:]
                    writer.writerow(out_data)

    return {'contents': out_str.getvalue().encode(), 'datatype': '/datatypes/csv', 'mimetype': 'text/csv', 'predecessors': [params[0]]}"""

    code_obj_data = create_data_object(
        name = 'Join CSV',
        ownerid = user_id5,
        description = 'Function to join CSVs',
        code = filter_func,
        comment = 'Inputs: (dobj_id, [join_table, join_column1, join_column2])'
    )
