#!/usr/bin/env python
import argparse
from typing import List
from dateutil import parser as dateparser

from knpl import Entity, Property, KNProgramSpace, KGPLFunction
import knpl
import matplotlib.pyplot as plt
from wikidataentities import WikidataLibrary

knps = KNProgramSpace("http://141.212.113.104:7200/repositories/2")
wd = WikidataLibrary(knps)

def renderSpouse(e: Entity):
    spouse = wd.P26
    print("Original entity  ", e)
    print("Entity spouse", e.get(spouse))

def plotTimeSeries(entities: List[Entity], prop: Property):
    pName = wd.NameProperty
    pTime = wd.P585
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


def show(entities: List[Entities]):
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
        entity = Entity.wikidataEntity(knps, args.qid)
        print("Entity:", entity)
    elif args.demo1:
        #usa = wd.Q30
        #canada = wd.Q16
        #getPopulation = wd.P1082
        #pointInTime = wd.P585

        #print("Canada population:", canada.getBest(getPopulation))

        #for rec in canada.getRelation(getPopulation):
        #    print(rec.get(getPopulation), rec.get(pointInTime))

        trump = wd.Q22686
        getSpouse = wd.P26
        print("All trump spouses:", trump.get(getSpouse))
        print("Current trump spouses:", trump.getBest(getSpouse))

        #obama = wd.Q76
        #getSpouse = wd.P26
        #print("Obama", obama)
        #print("Obama spouse", obama.getSpouse())

        #getGDP = wd.P2132
        #plotTimeline = wd.codelibrary.C99
        #plotTimeline(usa.getGDP().select(releaseid=8), canada.getGDP().select(releaseid=99))

        #computeInflation = aej.codelibrary.C9999
        #computeLocalWageInflationRate = aej.2015.shapiro.C1
        #print("Inflation for USA", computeInflation(usa.getGDP()))
        
        #from knpscode import CodeLibrary
        #code = CodeLibrary(knps)
        #result = code.compare(usa.getPopulation(), canada.getPopulation())
    elif args.demo2:
        #usa = wd.Q30
        #canada = wd.Q16
        
        obama = wd.Q76
        redsox = wd.Q213959
            
        getSpouse = wd.P26
        getPopulation = wd.P1082
        getHometown = wd.P19
            
        michele = obama.getSpouse()
        hometown = michele.getHometown()
        #usPop = usa.getPopulation()
        #canadaPop = canada.getPopulation()

        getCoach = Property.wikidataProperty(knps, "P286", "getCoach")
        coaches = redsox.get(getCoach)

        #print("USA:", usa)
        #print("USA population:", usPop)
        #print("Canada:", canada)
        #print("Canada population:", canadaPop)
        print("Obama:", obama)            
        print("Michele:", michele)
        print("Home town:", hometown)
        print("Team:", redsox)            
        print("Coach:", coaches)

    elif args.demo3:
        cityEntity = wd.Q515
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

        humanEntity = wd.Q5
        Human = humanEntity.asKNType()
        print("Type:", Human)        

        obama = wd.Q76
        instanceOf = wd.P31
        print("Obama:", obama)

        print("Obama instance:", obama.getInstanceOf())

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
        rs = KGPLFunction.registerFunction(knps, renderSpouse, knpl.KGPL_FUNC_DISPLAY_URI)

        pl = KGPLFunction.registerFunction(knps, plotTimeSeries, knpl.KGPL_FUNC_TIMESERIES_URI)

    elif args.demo5:
        rs = wd.F1
        obama = wd.Q76

        print("EXECUTING KGPL FUNCTION", rs)
        rs(obama)
        print("DONE EXECUTING KGPL FUNCTION")        

    elif args.demo6:
        plotTimeSeries = wd.F2
        #usa = wd.Q30
        #canada = wd.Q16
        #getPopulation = wd.P1082
        getGDP = Property.wikidataPropertyFromURI(knps, "http://www.wikidata.org/prop/P2131", "getGDP")

        print("Examples of getGDP():")
        for x in getGDP.getEntitiesWithThisProperty():
            print(x)

        #plotTimeSeries([canada], getPopulation)
        #plotTimeSeries([usa, canada], getGDP)

        
