import knps
import pandas
import numpy

if __name__=='__main__':
    # get the population of different countries in EU
    r = knps.ORM.createRelation('Q458')
    r.extend('P150',False,'Countries',label=True)
    r.extend('P1082',False, 'Total_population')
    r.changeFocus('Countries_P150')
    r.extend('P1082',False, 'population')
    r.query()

    knps.publish_new(r,"The population of different countries in European Union","EUData","Jack")

    # Created: KGPLValue with ID http://127.0.0.1:4242/val/9