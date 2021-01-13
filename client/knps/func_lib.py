import datetime
import requests
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
func_list = [temp0, temp1, temp2, temp3, temp4, temp5, get_entity_id, get_wikipedia_url, textual_summary, growth_rate, gdp_growth_perPresidentialTerm, time_transform]
