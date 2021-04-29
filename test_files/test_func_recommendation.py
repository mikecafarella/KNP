import knps
import pandas
import numpy
import requests
from bs4 import BeautifulSoup
from lxml import html
import json
import re

def test_red():
    r = knps.get_label_content('EUData')
    func_list = r.recommendFunction(['Countries_P150Label','population_P1082'])
    print(func_list)
    r.applyFunction(['Countries_P150Label','population_P1082'],func_list[-1])

def test_yellow():
    r = knps.get_label_content('EUData')
    func_list = r.recommendFunction(['Countries_P150Label','population_P1082','Total_population_P1082'])
    print(func_list)
    r.applyFunction(['Countries_P150Label','population_P1082','Total_population_P1082'],func_list[-1])

def test_none():
    r = knps.get_label_content('EUData')
    func_list = r.recommendFunction(['Countries_P150Label','population_P1082','Total_population_P1082','Basic ID'])
    print(func_list)

if __name__=='__main__':
    # test_yellow()
    test_none()