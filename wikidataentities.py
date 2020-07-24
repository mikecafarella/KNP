#!/usr/bin/env python

from knpl import GraphRepo, Entity, Property, KNProgramSpace, KGPLFunction

WIKIDATA_ENTITY_PREFIX = "http://www.wikidata.org/entity/%s"
WIKIDATA_PROPERTY_PREFIX = "http://www.wikidata.org/prop/%s"


class WikidataLibrary:
    """A Library that enables special access to Wikidata properties and entities"""
    def __init__(self, knps):
        self.knps = knps
        self.stdPropertyIds = {"name": "http://schema.org/name"}

    def getEntity(self, wikidataId):
        entityUri = WIKIDATA_ENTITY_PREFIX % str(wikidataId)
        return Entity.entityFromURI(self.knps, entityUri)

    def getProperty(self, wikidataId):
        propertyUri = WIKIDATA_PROPERTY_PREFIX % str(wikidataId)
        entityUri = WIKIDATA_ENTITY_PREFIX % str(wikidataId)
        return Property.propertyFromURI(self.knps, propertyUri, entityUri)

    def __getattr__(self, attrname):
        if attrname.find("Q") == 0:
            return self.getEntity(attrname)
        elif attrname.find("P") == 0:
            return self.getProperty(attrname)
        elif attrname in self.stdPropertyIds:
            uri = self.stdPropertyIds[attrname]
            return Property.propertyFromURI(self.knps, uri)
        else:
            raise AttributeError

