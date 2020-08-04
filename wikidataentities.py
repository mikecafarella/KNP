#!/usr/bin/env python

from knpl import GraphRepo, Entity, Property, KNProgramSpace, KGPLFunction
import streamlit as st
import requests

_API_ROOT = "https://www.wikidata.org/w/api.php"

WIKIDATA_ENTITY_PREFIX = "http://www.wikidata.org/entity/%s"
WIKIDATA_PROPERTY_PREFIX = "http://www.wikidata.org/prop/%s"


class WikidataLibrary:
    """A Library that enables special access to Wikidata properties and entities"""
    def __init__(self, knps):
        self.knps = knps
        self.stdPropertyIds = {"name": "http://schema.org/name"}
        self.finder = Finder(knps)

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
            print("Can't find", attrname)
            raise AttributeError

class Finder:
    def __init__(self, knps):
        self.knps = knps

    def _search(self, searchStr, searchType, limit=10):
        """Search for an entity on Wikidata using a label fragment"""

        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": "en",
            "search": searchStr,
            "limit": limit,
            "type": searchType
            }
        info = requests.get(_API_ROOT, params=params).json()["search"]
        rst = []
        for _, i in enumerate(info):
            rst.append(i)
        return rst

    def search_entity(self, searchStr, limit=10):
        return self._search(searchStr, "item", limit=limit)

    def search_property(self, searchStr, limit=10):
        return self._search(searchStr, "property", limit=limit)



