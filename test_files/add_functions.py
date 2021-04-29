import knps
import pandas
import numpy
import requests
from bs4 import BeautifulSoup
from lxml import html
import json
import re

def popOverCountry(df):
    import matplotlib.pyplot as plt
    x = df[df.columns[0]]
    y = df[df.columns[1]]
    y = y.apply(lambda x: int(x))
    plt.scatter(x,y)
    plt.title(label='Population of European Union countries')
    temp = plt.gca().xaxis
    for item in temp.get_ticklabels():
        item.set_rotation(90)
    plt.savefig("temp.png")

def popOverCountry_red(df):
    import matplotlib.pyplot as plt
    x = df[df.columns[0]]
    y = df[df.columns[1]]
    y = y.apply(lambda x: int(x))
    plt.scatter(x,y,c='red')
    plt.title(label='Population of European Union countries')
    temp = plt.gca().xaxis
    for item in temp.get_ticklabels():
        item.set_rotation(90)
    plt.savefig("temp_red.png")

def popOverCountry_3col(df):
    import matplotlib.pyplot as plt
    x = df[df.columns[0]]
    y = df[df.columns[1]]
    y = y.apply(lambda x: int(x))
    plt.scatter(x,y,c='yellow')
    plt.title(label='Population of European Union countries')
    temp = plt.gca().xaxis
    for item in temp.get_ticklabels():
        item.set_rotation(90)
    plt.savefig("temp_yellow.png")

def popOverCountry_4col(df):
    import matplotlib.pyplot as plt
    x = df[df.columns[0]]
    y = df[df.columns[1]]
    y = y.apply(lambda x: int(x))
    plt.scatter(x,y,c='green')
    plt.title(label='Population of European Union countries')
    temp = plt.gca().xaxis
    for item in temp.get_ticklabels():
        item.set_rotation(90)
    plt.savefig("temp_green.png")

def dummy(df):
    pass

def add_10_dummy_function():
    for i in range(10):
        tempFunc = knps.FunctionWithSignature(dummy,[str])
        knps.publish_new(tempFunc, "dummy function")

def add_func_3col():
    createPopulationOverCountryVisualization = knps.FunctionWithSignature(popOverCountry_3col,[str, knps.ORM.WikiDataProperty(['P1082']), int])
    knps.publish_new(createPopulationOverCountryVisualization, "visual function", '3col function', 'Jack')

def add_dummy_4col():
    createPopulationOverCountryVisualization = knps.FunctionWithSignature(popOverCountry_4col,[str, knps.ORM.WikiDataProperty(['P1082']), knps.ORM.WikiDataProperty(['P1082']), str])
    knps.publish_new(createPopulationOverCountryVisualization, "visual function", '3col function', 'Jack')

if __name__ =="__main__":
    # add_10_dummy_function()
    add_func_3col()
    
    