from __future__ import annotations
from kgpl.kgpl import *
import KGType

county_population = KGPLValue.LoadFromURL("localhost/80987112-5451-486e-ae78-f61eda43975d")
county_cases = KGPLValue.LoadFromURL("localhost/20eafb7e-7c1d-4902-adcc-fd887cc91f6f")

def combine_county_data(value1, value2):
    df = value1.set_index("county_name").join(value2.set_index("County"))
    return df
combine_county_data = kgfunc(combine_county_data)

county = combine_county_data(county_population, county_cases)

# county.showLineageTree()

def get_correlations(df):
    corr = df.corr(method="pearson")
    return corr

get_correlations = kgfunc(get_correlations)

corr = get_correlations(county)
print(corr)
