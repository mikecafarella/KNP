#!/usr/bin/env python
import argparse

from knpl import Entity, Property, KNProgramSpace
from wikidataentities import WikidataLibrary

knps = KNProgramSpace("http://141.212.113.104:7200/repositories/2")
wd = WikidataLibrary(knps)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Try out a few GraphDB-backed items")
    parser.add_argument("--qid", help="Which QID to fetch")
    parser.add_argument("--demo1", dest="demo1", action="store_true", help="Whether to run demo 1")
    parser.add_argument("--demo2", dest="demo2", action="store_true", help="Whether to run demo 2")
    parser.add_argument("--demo3", dest="demo3", action="store_true", help="Whether to run demo 3")            

    args = parser.parse_args()

    if not args.qid and not args.demo1 and not args.demo2 and not args.demo3:
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
        
            

        
