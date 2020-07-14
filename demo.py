#!/usr/bin/env python
import argparse

from knpl import Entity, Property, KNProgramSpace
from wikidataentities import WikidataLibrary

knps = KNProgramSpace("http://141.212.113.104:7200/repositories/1")
wd = WikidataLibrary(knps)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Try out a few GraphDB-backed items")
    parser.add_argument("--qid", help="Which QID to fetch")
    parser.add_argument("--demo1", dest="demo1", action="store_true", help="Whether to run demo 1")
    parser.add_argument("--demo2", dest="demo2", action="store_true", help="Whether to run demo 2")        

    args = parser.parse_args()

    if not args.qid and not args.demo1 and not args.demo2:
        parser.print_help()
    elif args.qid:
        print("Fetching Wikidata object " + args.qid)
        entity = Entity.wikidataEntity(knps, args.qid)
        print("Entity:", entity)
    elif args.demo1:
        usa = wd.Q30
        canada = wd.Q16
        getPopulation = wd.P1082        
        canadaPop = canada.getPopulation()        
        #from knpscode import CodeLibrary
        #code = CodeLibrary(knps)
        #result = code.compare(usa.getPopulation(), canada.getPopulation())
        
    elif args.demo2:
        usa = wd.Q30
        canada = wd.Q16
        
        obama = wd.Q76
        redsox = wd.Q213959
            
        getSpouse = wd.P26
        getPopulation = wd.P1082
        getHometown = wd.P19
            
        michele = obama.getSpouse()
        hometown = michele.getHometown()
        usPop = usa.getPopulation()
        canadaPop = canada.getPopulation()

        getCoach = Property.wikidataProperty(knps, "P286", "getCoach")
        coaches = redsox.get(getCoach)

        print("USA:", usa)
        print("USA population:", usPop)
        print("Canada:", canada)
        print("Canada population:", canadaPop)
        print("Obama:", obama)            
        print("Michele:", michele)
        print("Home town:", hometown)
        print("Team:", redsox)            
        print("Coach:", coaches)

            
