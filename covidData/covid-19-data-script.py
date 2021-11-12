import pandas as pd
import os
import sys
import time
sys.path.append("../cli/src/knps")
from knps import get_version
import subprocess
import pathlib

sys.path.pop()

parent_directory = str(pathlib.Path(__file__).parent.resolve())

##Uncomment these lines if it has already been cloned
# os.system("rm covid-19-data")
# os.system("git clone https://github.com/nytimes/covid-19-data.git")

covid_19_folder_path = parent_directory + "/covid-19-data"

output_folder_path = parent_directory + "/covid-19-data-output"

## CHANGE THIS POSSIBLY ~
os.system("rm ~/.knps_dir_db") ##NEED TO DO THIS SO IT DOES NOT THINK THINGS R INACCURATELY PROCCESSED
os.system("rm -r " + output_folder_path)
os.system("mkdir " + output_folder_path)
os.system("knps --watch " + output_folder_path)

us_data = pd.read_csv(covid_19_folder_path + "/us.csv")
us_state_data = pd.read_csv(covid_19_folder_path + "/us-states.csv")
us_county_data = pd.read_csv(covid_19_folder_path + "/us-counties.csv")
college_data = pd.read_csv(covid_19_folder_path + "/colleges/colleges.csv") ## MAY 26, 2021 UPDATE
excess_deaths_data = pd.read_csv(covid_19_folder_path + "/excess-deaths/deaths.csv") ## UP to JAN 18, 2021
mask_use_data = pd.read_csv(covid_19_folder_path + "/mask-use/mask-use-by-county.csv") ## July 20, 2020 UPDATE
prison_facility_data = pd.read_csv(covid_19_folder_path + "/prisons/facilities.csv") ## MARCH 2020 - MARCH 2021
prison_systems_data = pd.read_csv(covid_19_folder_path + "/prisons/systems.csv") ## ^^

## TODO POSSIBILY INCLUDE ROLLING DATA AS WELL

def updateFile(outfilepath, curr_date, data):
	temp = data[data.date <= curr_date]
	temp.to_csv(outfilepath, index = False)

all_dates = us_data.date.unique()
k = 0
start_time = time.time()
sec_time = time.time()
print("There are ", len(all_dates), "days total.")
for curr_date in all_dates:
	# print(curr_date)
	if curr_date == "2020-07-20":
		# print("MAKE USE DATA ...")
		mask_use_data.to_csv(output_folder_path + "/mask-use-by-country.csv", index = False)
	if curr_date == "2021-05-26":
		# print("COLLEGE DATA ...")
		college_data.to_csv(output_folder_path + "/colleges.csv", index = False)
	if curr_date == "2021-01-18":
		# print("EXCESS DEATH DATA DATA ...")
		excess_deaths_data.to_csv(output_folder_path + "/excess_deaths.csv", index = False)
	if curr_date == "2021-03-01":
		# print("PRISONS DATA ...")
		prison_facility_data.to_csv(output_folder_path + "/prisons-facilities.csv", index = False)
		prison_systems_data.to_csv(output_folder_path + "/prisons-systems.csv", index = False)
	updateFile(output_folder_path + "/us_data.csv", curr_date, us_data)
	updateFile(output_folder_path + "/us_state_data.csv", curr_date, us_state_data)
	updateFile(output_folder_path + "/us_county_data.csv", curr_date, us_county_data)
	k += 1
	# os.system("knps --sync")
	# print("\n\n\n\n\n\n")
	subprocess.check_output('knps --sync', shell=True) 
	if k % 10 == 0: 
		print(f"--------------------------------{k}--------------------------------")
		print("Total time: ", time.time()-start_time)
		print("Avg Section time: ", (time.time()-sec_time)/10)
		sec_time = time.time()
