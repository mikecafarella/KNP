#!/usr/bin/env python
import argparse
from typing import List
from dateutil import parser as dateparser

from knpl import Entity, Property, KNProgramSpace, KGPLFunction
from kgdata import KGData
import knpl
import matplotlib.pyplot as plt


kgdata = KGData(KNProgramSpace("http://141.212.113.104:7200/repositories/2"))

def renderSpouse(e: Entity):
    spouse = kgdata.wd.P26
    print("Original entity  ", e)
    print("Entity spouse", e.get(spouse))

def plotTimeSeries(entities: List[Entity], prop: Property):
    pName = kgdata.wd.name
    pTime = kgdata.wd.P585
    fig, axs = plt.subplots()
    axs.set_xlabel("Time")
    axs.set_ylabel(prop.get(pName))
    axs.set_title(prop.get(pName))
    
    for e in entities:
        tuples = []
        for x in e.getRelation(prop):
            try:
                d = dateparser.parse(str(x.get(pTime)))
                y = float(x.get(prop))
                tuples.append((d, y))
            except Exception:
                pass
        tuples.sort()
        xvals = list(map(lambda t: t[0], tuples))
        yvals = list(map(lambda t: t[1], tuples))
        axs.plot(xvals, yvals, label=e.label())
    axs.legend()
    fig.show()


def show(entities: List[Entity]):
    # grab images
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Try out a few GraphDB-backed items")
    parser.add_argument("--qid", help="Which QID to fetch")
    parser.add_argument("--demo1", dest="demo1", action="store_true", help="Whether to run demo 1")
    parser.add_argument("--demo2", dest="demo2", action="store_true", help="Whether to run demo 2")
    parser.add_argument("--demo3", dest="demo3", action="store_true", help="Whether to run demo 3")
    parser.add_argument("--demo4", dest="demo4", action="store_true", help="Whether to run demo 4")
    parser.add_argument("--demo5", dest="demo5", action="store_true", help="Whether to run demo 5")
    parser.add_argument("--demo6", dest="demo6", action="store_true", help="Whether to run demo 6")                        

    args = parser.parse_args()

    if not args.qid and not args.demo1 and not args.demo2 and not args.demo3 and not args.demo4 and not args.demo5 and not args.demo6:
        parser.print_help()
    elif args.qid:
        print("Fetching Wikidata object " + args.qid)
        entity = kgdata.wd.getEntity(args.qid)
        print("Entity:", entity)
    elif args.demo1:
        trump = kgdata.wd.Q22686
        spouse = kgdata.wd.P26
        print("All trump spouses:", trump.get(spouse))
        print("Current trump spouses:", trump.getBest(spouse))

        #computeInflation = aej.codelibrary.C9999
        #computeLocalWageInflationRate = aej.2015.shapiro.C1
        #print("Inflation for USA", computeInflation(usa.getGDP()))
        
        #from knpscode import CodeLibrary
        #code = CodeLibrary(knps)
        #result = code.compare(usa.getPopulation(), canada.getPopulation())
    elif args.demo2:
        obama = kgdata.wd.Q76
        redsox = kgdata.wd.Q213959
            
        spouse = kgdata.wd.P26
        population = kgdata.wd.P1082
        hometown = kgdata.wd.P19
            
        michele = obama.get(spouse)
        hometown = michele.get(hometown)

        coach = kgdata.wd.P286
        coaches = redsox.get(coach)

        print("Obama:", obama)            
        print("Michele:", michele)
        print("Home town:", hometown)
        print("Team:", redsox)            
        print("Coach:", coaches)

    elif args.demo3:
        cityEntity = kgdata.wd.Q515
        City = cityEntity.asKNType()
        print("Type:", City)
        #for x in City.getExamples():
        #    print(x)

        #print()
        #print()
        #print()
        #print("---------------------------------------")
        #print()
        #print()
        #print()

        humanEntity = kgdata.wd.Q5
        Human = humanEntity.asKNType()
        print("Type:", Human)        

        obama = kgdata.wd.Q76
        instanceOf = kgdata.wd.P31
        print("Obama:", obama)

        print("Obama instance:", obama.get(instanceOf))

        print("Is Obama a Human?", isinstance(obama, Human))
        print("Is Obama a City?", isinstance(obama, City))


        print("Typical properties of " + str(Human))
        for x in Human.getTypicalProperties():
            print(x)

        print()
        print("Examples of " + str(Human))
        for x in Human.getExamples():
            print(x)

    elif args.demo4:
        rs = kgdata.registerFunction(renderSpouse, kgdata.KGPL_FUNC_DISPLAY_ID)

        pl = kgdata.registerFunction(plotTimeSeries, kgdata.KGPL_FUNC_TIMESERIES_ID)

    elif args.demo5:
        rs = kgdata.funcs.F1
        obama = kgdata.wd.Q76

        print("EXECUTING KGPL FUNCTION", rs)
        rs(obama)
        print("DONE EXECUTING KGPL FUNCTION")        

    elif args.demo6:
        plotTimeSeries = kgdata.funcs.F2
        usa = kgdata.wd.Q30
        canada = kgdata.wd.Q16
        getPopulation = kgdata.wd.P1082
        getGDP = kgdata.wd.P2131

        print("Examples of getGDP():")
        for x in getGDP.getEntitiesWithThisProperty():
            print(x)

        plotTimeSeries([canada], getPopulation)
        plotTimeSeries([usa, canada], getGDP)

        
