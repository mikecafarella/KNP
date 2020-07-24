#!/usr/bin/env python

from knpl import GraphRepo, Entity, Property, KNProgramSpace, KGPLFunction

class WikidataLibrary:
    def __init__(self, knps):
        self.knps = knps
        self.stdPropertyIds = {"P19": ("wd", "getHometown"),
                               "P31": ("wd", "getInstanceOf"),
                               "P18": ("wd", "getImage"),
                               "P26": ("wd", "getSpouse"),
                               "P1082": ("wd", "getPopulation"),
                               "NameProperty": ("http://schema.org/name", "getName"),
                               "P585": ("wd", "getPointInTime"),
                               "P1963": ("wd", "getTypicalProperties")}

    def __getattr__(self, attrname):
        if attrname.find("Q") == 0:
            return Entity.wikidataEntity(self.knps, attrname)
        elif attrname.find("F") == 0:
            return KGPLFunction.fetchStandardFunction(self.knps, attrname)
        elif attrname.find("P") == 0:
            if attrname in self.stdPropertyIds:
                src, propertyLabel = self.stdPropertyIds[attrname]
                return Property.wikidataProperty(self.knps, attrname, propertyLabel)
        elif attrname in self.stdPropertyIds:
            srcUri, propertyLabel = self.stdPropertyIds[attrname]
            return Property.wikidataPropertyFromURI(self.knps, srcUri, propertyLabel)
        else:
            raise AttributeError

