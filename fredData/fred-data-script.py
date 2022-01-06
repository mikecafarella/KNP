
from full_fred.fred import Fred
import os

key_file = open('api_key.txt', 'r')
API_KEY = key_file.readline()
key_file.close()
os.environ['FRED_API_KEY'] = API_KEY.strip()
# ideally we just use the constructor and pass in the file name, 
# but that wasn't working so had to use this hack
fred = Fred()

# iterate thru categories and get series ids
# 0 is the root category
categories = fred.get_child_categories(0)
print(categories)

