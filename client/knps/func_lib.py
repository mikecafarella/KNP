import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup

func_list = []

def add_func(func):
    func_list.append(func)

def func_num():
    return len(func_list)

def temp0(x):
    return x

def temp1(name: str):
    return name.split(' ')[0]

def temp2(name: str):
    return name.split(' ')[-1]

def temp3(birth, death):
    if birth == 'NA':
        return 'NA'
    if death == 'NA':
        date_time_obj = datetime.datetime.strptime(birth[:4], '%Y')
        return datetime.datetime.now().year - date_time_obj.year
    else:
        return datetime.datetime.strptime(death[:4], '%Y').year - datetime.datetime.strptime(birth[:4], '%Y').year

def temp4(x):
    url = 'https://en.wikipedia.org/wiki/'
    for word in x.split(' '):
        url += (word + '_')
    url = url[:-1]
    s = requests.session()
    r = s.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    results = soup.find(id='bodyContent')
    results = results.find(id='mw-content-text')
    results = results.find_all('p')
    if len(results) > 1:
        return results[0].text.split('.')[0]
    return results[0].text.split('.')[0]

def temp5(x):
    if x == 'NA':
        return 'NA'
    url = 'https://www.google.com/maps/place/'
    for word in x.split(' '):
        url += (word + '%20')
    url = url[:-3]
    # r = requests.get(url)
    return url

# get_entity_id(url)
# return the entity if (ex. Q76) of an entity
# F6
def get_entity_id(url):
    return url.split('/')[-1]

# return the wikipedia url for an entity
# F7
def get_wikipedia_url(wikidata_id):
    lang = 'en'
    url = (
        'https://www.wikidata.org/w/api.php'
        '?action=wbgetentities'
        '&props=sitelinks/urls'
        f'&ids={wikidata_id}'
        '&format=json')
    json_response = requests.get(url).json()
    entities = json_response.get('entities')
    if entities:
        entity = entities.get(wikidata_id)
        if entity:
            sitelinks = entity.get('sitelinks')
            if sitelinks:
                sitelink = sitelinks.get(f'{lang}wiki')
                if sitelink:
                    wiki_url = sitelink.get('url')
                    if wiki_url:
                        return requests.utils.unquote(wiki_url)
    return None

# return the textual_summary of the wikipedia page
# F8
def textual_summary(url):
    print(url)
    if not url:
        return "None"
    s = requests.session()
    r = s.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    results = soup.find(id='bodyContent')
    results = results.find(id='mw-content-text')
    results = results.find_all('p')
    i = 0
    for i in range(len(results)):
        if results[i].text != '\n':
            break
    return results[i].text

# return the annual GDP growth rate of a country
# F9
def growth_rate(df, name, gdp, time):
    df.sort_values(by=[time], ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df[name] = df[gdp]
    for i in range(len(df)-1):
        df.loc[i, name] = (
            (float(df.loc[i, gdp]) - float(df.loc[i+1, gdp])) / float(df.loc[i+1, gdp]))
    df.loc[len(df)-1, name] = float('NaN')
    return df

# return none-normalized, none-compounding annual GDP growth rate based on presidential term
# F10

def gdp_growth_perPresidentialTerm(df, name, president, end_time, start_time):
    df = df[[president, end_time, start_time]]
    df[end_time] = df[end_time].apply(transform)
    df[start_time] = df[start_time].apply(transform)

    df[name] = 0
    for index, row in df.iterrows():
        df.loc[index, name] = r.df[(r.df['GDP_point_in_time_P2131_P585'] >= row[start_time]) & (
            r.df['GDP_point_in_time_P2131_P585'] <= row[end_time])]['growth_rate'].sum()
    return df

# transform wikidata time to have year only
# F11
def time_transform(time):
    return time[0:4]

# a table function that calculates the boxoffice fraction each movie occupies in its director's lifetime total
# returns a dataframe with the additional column "fraction"
# F12
def boxoffice_fraction(df, name, film, director, film_gross):
    #film_gross = pd.read_csv('boxoffice.csv')
    film_gross.columns = ['rank', film, 'studio', 'gross', 'year']
    film_gross[film] = film_gross[film].astype(str)
    df[film] = df[film].astype(str)
    new_df = film_gross.merge(df, on=film)  # merge with external data
    new_df.drop_duplicates(subset=['rank'], inplace=True)
    sum_df = new_df.groupby([director]).sum()
    sum_df.columns = ['rk', 'total', 'y']
    final_df = new_df.merge(sum_df, on=director)
    final_df[name] = final_df.apply(lambda x: '%.2f%%' % (x['gross'] / x['total'] * 100), axis=1)
    sel = [str(x) for x in df.columns]
    sel.append(name)
    return final_df[sel]

# a function that converts dollars to euro for a specific year
# F13
# def dollar2euro(df, name, dollar, time):
#     r = createRelation('Q4917')
#     r.extend('P2284', False, 'euro', rowVerbose=True, colVerbose=True)
#     r.query()
#     helper_df = r.df
#     r.df['euro_point_in_time_P2284_P585'] = r.df['euro_point_in_time_P2284_P585'].apply(lambda x: str(x)[:4])
#     df[time] = df[time].apply(lambda x: str(x)[:4])
#     r.df.rename(columns={'euro_point_in_time_P2284_P585':time, 'euro_P2284':name}, inplace=True)
#     df = df.merge(r.df, on=time)
#     df['euro']=df[[dollar, 'euro']].apply(lambda x:float(x[dollar])*float(x['euro']),axis=1)
#     return df

'''
Inputs:
- string containing longitude, latitude, and other extraneous characters
- OR longitude latitude tuple
Output: (float longitude, float latitude) tuple
'''
def parse_lon_lat(lon_lat):
    # if the input value is empty
    if lon_lat == 'NA':
        return 'NA'

    # if the input value looks like the format from wikidata
    if lon_lat[:6]=='Point(':
        entities = lon_lat[6:-1].split(' ')
        lon = float(entities[0])
        lat = float(entities[1])

    # if it's already been formatted as a tuple
    if len(lon_lat) == 2 and type(lon_lat) is tuple:
        lon, lat = lon_lat
        # if lon and lat values are valid
        if type(lon) is float and type(lat is float):
            if lon >= -180 and lon <= 180:
                if lat >= -90 and lat <= 90:
                    return lon_lat
        return 'NA' # if it's an invalid tuple

    return(lon, lat)

'''
Inputs:
- 20-character-string wikidata format
- OR the 10-character yyyy-mm-dd format
Output:
- 10-character yyyy-mm-dd format
'''
def parse_date(date):
    # if the input value is empty
    if date=='NA':
        return 'NA'

    # if the input value looks like the format from wikidata
    if len(date)==20:
        return date[:10]

    # if it's already been formatted as a string
    if len(date)==10 and isinstance(date, str) and date[4]=='-' and date[-3]=='-':
        return date

    # if the input value is empty, an invalid string, or other
    return 'NA'

'''
Inputs:
- pandas datafrae df from KNP SPARQL relation
- string name of column that contains dates
- string name of column that contains coordinates
- string name of column that contains entity names
- string title of map
'''
import geopandas
import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt
def arrow_map(df, date_col_name, coord_col_name, entity_name, plot_title):

    df = df.reset_index(drop=True)

    lon_lat_parsed = [parse_lon_lat(x) for x in df[coord_col_name]]
    date_parsed = [parse_date(x) for x in df[date_col_name]]
    names = df[entity_name]

    date_coords_list = [(date, coords, name) for date, coords, name in zip(date_parsed, lon_lat_parsed, names)]
    date_coords_list_sorted = sorted(date_coords_list)
    lats = [lat for lon, lat in lon_lat_parsed]
    lons = [lon for lon, lat in lon_lat_parsed]
    gdf = geopandas.GeoDataFrame(df,
                                 geometry=geopandas.points_from_xy(lats, lons))
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    ax = world.plot(
        color='white', edgecolor='black', figsize=(18, 10))
    gdf.plot(ax=ax, color='red')

    travel_log = []
    for ind in range(len(date_coords_list_sorted)-1):

        date, coords, name = date_coords_list_sorted[ind]
        travel_log.append(date + '\t' + name)

        _, coords_next, _ = date_coords_list_sorted[ind + 1]
        if coords_next==coords:
            continue
        x, y = coords
        x_next, y_next = coords_next

        style = "Simple, tail_width=1.5, head_width=7, head_length=20"
        base_alpha = 0.15
        kw = dict(arrowstyle=style, color='xkcd:dark blue',
                  alpha=((1-base_alpha)/(len(df)))*ind+base_alpha)
        rad = (1/len(date_coords_list_sorted))*ind
        a = patches.FancyArrowPatch((x, y), (x_next, y_next),
                                     connectionstyle="arc3,rad=%s" % str(rad), **kw)
        plt.gca().add_patch(a)

    if max(lons)-min(lons) <= 10:
        subdivision = 1
    elif max(lons)-min(lons) <= 20:
        subdivision = 2
    elif max(lons)-min(lons) <= 50:
        subdivision = 5
    else:
        subdivision = 10

    xmin = round(min(lons)-subdivision)
    xmax = round(max(lons)+subdivision)
    ymin = round(min(lats)-subdivision)
    ymax = round(max(lats)+subdivision)
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    plt.xticks(np.arange(xmin, xmax+1, subdivision), fontsize=15)
    plt.yticks(np.arange(ymin, ymax+1, subdivision), fontsize=15)
    plt.title(plot_title, fontsize=20)
    plt.show()

    for t in travel_log:
        print(t)

func_list = [temp0, temp1, temp2, temp3, temp4, temp5, get_entity_id, get_wikipedia_url,
             textual_summary, growth_rate, gdp_growth_perPresidentialTerm, time_transform,
            boxoffice_fraction, parse_lon_lat, parse_date, arrow_map]
