#!/usr/bin/env python

from knpl import GraphRepo, Entity, Property, KNProgramSpace

class WikidataLibrary:
    def __init__(self, knps):
        self.knps = knps
        self.stdPropertyIds = {"P19": "getHometown",
                               "P31": "getInstanceOf",
                               "P26": "getSpouse",
                               "P1082": "getPopulation",
                               "P585": "getPointInTime",
                               "P1963": "getTypicalProperties"}

    def __getattr__(self, attrname):
        if attrname.find("Q") == 0:
            return Entity.wikidataEntity(self.knps, attrname)
        elif attrname.find("P") == 0:
            if attrname in self.stdPropertyIds:
                return Property.wikidataProperty(self.knps, attrname, self.stdPropertyIds[attrname])
        else:
            raise AttributeError

