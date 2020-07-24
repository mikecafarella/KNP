#!/usr/bin/env python

from wikidataentities import WikidataLibrary
from knpl import KGPLFunction

KGPL_FUNC_PREFIX = "http://kgpl.org/function/%s"

KGPL_FUNC_DISPLAY_ID = "F1"
KGPL_FUNC_TIMESERIES_ID = "F2"

class KGData:
    """A library of all the KG data in the universe, with special
    accessors for special namespaces, like wd for Wikidata"""
    def __init__(self, knps):
        self.knps = knps
        self.wd = WikidataLibrary(knps)
        self.funcs = Funcs(knps)

class Funcs:        
    def __init__(self, knps):
        self.knps = knps
        
    def registerFunction(self, func, funcId):
        uri = KGPL_FUNC_PREFIX % str(funcId)
        return KGPLFunction.registerFunction(knps, func, uri)

    def __getattr__(self, attrname):
        if attrname.find("F") == 0:
            uri = KGPL_FUNC_PREFIX % str(attrname)
            return KGPLFunction.fetchFunction(self.knps, uri)

    
