import knps
import pandas
import numpy

def info(country: str, population: numpy.int64):
    result = "The population of " + country + " is " + str(population) + ", taking " + " percent of EU."
    print(result)
    return result

# def info(country: str, population: float, percentage: float):
#     result = "The population of " + country + " is " + str(population) + ", taking " + str(percentage) + " percent of EU."
#     return result

def test2():
    val = knps.get_label_content('Q458')
    # print(type(val.df['population_P1082'][0]))

    val.extendWithFunction(['Countries_P150Label','population_P1082'],info,'Info')

def test1():
    r = knps.ORM.createRelation('Q458')
    r.extend('P150',False,'Countries',label=True)
    r.extend('P1082',False, 'Total_population')
    r.changeFocus('Countries_P150')
    r.extend('P1082',False, 'population')
    r.query()
    # print(type(r.df['population_P1082'][0]))

    js_json_to = r.df.to_json()
    js_read_back = pandas.read_json(js_json_to)
    print(type(r.df['population_P1082'][0]))
    print(type(js_read_back['population_P1082'][0]))



    # r.df.to_html('dff.html')
    # knps.publish_new(r,"Q458 comment","Q458","Alice")

if __name__ =="__main__":
    # test1()
    test2()
