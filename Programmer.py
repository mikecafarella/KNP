"""
The USER wants to generate a heatmap of areas in potential need of
staff.  The USER wants to generate examine the relationship between
each hospital's caseload and the hospital's medical-staff count.
"""

import requests
import pandas as pd
import datacommons as dc
from kgpl.kgpl import *
import KGType
dc.set_api_key('AIzaSyBzz86DTFr34nAv5WCHUmfIXEWZ-xFJX9A')

# Step 1: The USER grabs a list of Hospitals from the KG.
# Step 2: The USER grabs the number of medical staff from each Hospital entity.
# Step 3: The USER grabs the lat/long from each Hospital.
# Step 4: The USER grabs state of MICHIGAN has published per-hospital Covid data via a MEDICAL-KG.
# The USER grab (county, # of cases, # of reported deaths) data.
# Step 5: The USER now creates a new dataset: (Hospital, covid-per-medical-staff).

"""Yuze's idea:
1. Get (county, # of cases, # of reported deaths) data.
2. Get (county, population) data.
3. Maybe also (county, the population of the elder) data.
4. Combine them and share by using KGPLVariable
5. Another programmer comes in. He could analize the correlations in the data.
"""

# （county in Michigan, population, med_age)
county = pd.DataFrame({'state': ['geoId/26']})  # Michian
county['county'] = county['state'].map(dc.get_places_in(county['state'], 'County'))
county = county.explode("county").reset_index(drop=True)
county['county_name'] = county['county'].map(dc.get_property_values(county['county'], 'name'))
county = county.explode('county_name').reset_index(drop=True)
# constraining_properties = {'age': 'Years45To54'}
county['all_persons_pop'] = county['county'].map(dc.get_populations(county['county'], 'Person'))

county['count'] = county['all_persons_pop'].map(dc.get_observations(county['all_persons_pop'], 
    'count',
    'measuredValue',
    '2018', 
    measurement_method='CensusACS5yrSurvey'))
county['med_age'] = county['all_persons_pop'].map(dc.get_observations(county['all_persons_pop'], 
    'age',
    'medianValue',
    '2018', 
    measurement_method='CensusACS5yrSurvey'))
county['county_name'] = county['county_name'].map(lambda x: x.split(" ")[0])
county.drop(['state', 'county', 'all_persons_pop'], axis=1, inplace=True)

county_population = KGPLValue(county, lineages=[Lineage.InitFromKG("datacommons")])
county_population.register('localhost')
print(county_population.url)


# (county, # of cases, # of reported deaths)
url = 'https://www.michigan.gov/coronavirus/0,9753,7-406-98163-520743--,00.html'
page = requests.get(url)
df = pd.read_html(page.content)[0]
df.drop(df.index[-5:], inplace=True)

county_cases = KGPLValue(df)
county_cases.register('localhost')
print(county_cases.url)
