#!/usr/bin/env python
import sparql
from abc import ABC, abstractmethod

WIKIDATA_PROPERTY_PREFIX = "http://www.wikidata.org/prop/direct/%s"
INSTANCE_OF_URI = "http://www.wikidata.org/prop/direct/P31"
WIKIDATA_ENTITY_PREFIX = "http://www.wikidata.org/entity/%s"
LABEL_PROPERTY = "http://www.w3.org/2000/01/rdf-schema#label"


#
#
#
class KNType(ABC):
    pass
    #def __instancecheck__(self, instance):
    #    return isinstance(instance, Entity) and self.entity in instance.get(wd.P31)


#
#
#
class KNProgramSpace:
    def __init__(self, graphRepoURI):
        self.gr = GraphRepo(self, graphRepoURI)
        self.registeredProperties = {}

    def registerProperty(self, prop, accessorName):
        self.registeredProperties[accessorName] = prop

    def getRegisteredProperty(self, accessorName):
        return self.registeredProperties.get(accessorName, None)

    def __eq__(self, other):
        return isinstance(other, KNProgramSpace) and self.gr == other.gr

    def close(self):
        self.gr.close()

#
#
#
class PropertyException(Exception):
    "Throw this exception if the entity property is missing"
    def __init__(self, entity, prop):
        self.entity = entity
        self.prop = prop

    def __str__(self):
        return "No property for (" + str(self.entity) + "." + str(self.prop) + ")"

class MissingDataException(PropertyException):
    "Throw this exception if the entity property SHOULD be there, but is missing"    
    def __init__(self, entity, prop):
        super().__init__(entity, prop)

class InappropriatePropertyException(PropertyException):  
    "Throw this exception if entity property SHOULDN'T be there, but was called anyway"      
    def __init__(self, entity, prop):
        super().__init__(entity, prop)

class UnknownPropertyException(PropertyException):
    "Throw this exception if the requested property does not exist"
    def __init__(self, entity, attrname):
        super().__init__(entity, attrname)

#
#
#
class Entity:
    "Entity representative"
    def __init__(self, knps, entityUri):
        self.knps = knps
        self.entityUri = entityUri
        self.facts = None

    @classmethod
    def wikidataEntity(cls, knps, wikidataId):
        return cls(knps, WIKIDATA_ENTITY_PREFIX % wikidataId)

    def __populate__(self):
        self.facts = {}

        for prop, val in self.knps.gr.getLiteralFacts(self.entityUri):
            self.facts.setdefault(prop, []).append(val)

        for prop, val in self.knps.gr.getEntityFacts(self.entityUri):
            self.facts.setdefault(prop, []).append(val)

    def __eq__(self, other):
        return self.knps == other.knps and self.entityUri == other.entityUri
            
    def get(self, prop):
        if self.facts is None:
            self.__populate__()

        x = self.facts.get(prop.getPropertyUri())
        if x is None:
            self.__handleMissingProperty__(prop)
            
        if len(x) == 1:
            return x[0]
        else:
            return x     

    def asKNType(self):
        "Synthesize a Python class that captures the current Entity"
        if self.facts is None:
            self.__populate__()

        clsName = "_".join(self.facts.get(LABEL_PROPERTY))
        clsBases = (KNType,)
        #clsBases = (KNThing,)        

        @classmethod
        def getExamples(cls):
            return cls.entity.knps.gr.getExamplesOfEntity(cls.entity.entityUri)

        @classmethod
        def getTypicalProperties(cls):
            return cls.entity.get(cls.typicalPropertiesProperty)

        @classmethod
        def __instancecheck__(cls, instance):
            print("instance test")
            return cls.entity.get(cls.instanceProperty) == instance
        
        clsAttrs = {"entity": self,
                    "typicalPropertiesProperty": Property.wikidataProperty(self.knps, "P1963", "getTypicalProperties"),
                    "instanceProperty": Property.wikidataProperty(self.knps, "P31", "getInstanceOf"),                    
                    "getExamples": getExamples,
                    "__instancecheck__": __instancecheck__,
                    "getTypicalProperties": getTypicalProperties}
        
        newCls = type(clsName, clsBases, clsAttrs)
        return newCls

    def __str__(self):
        if self.facts is None:
            self.__populate__()

        return " ".join(self.facts.get(LABEL_PROPERTY))

    def __repr__(self):
        return self.__str__()

    def __getattr__(self, attr):
        registeredProp = self.knps.getRegisteredProperty(attr)
        if registeredProp is not None:
            return EntityPropertyGetter(self, registeredProp)
        else:
            raise AttributeError()
        
    def __handleMissingProperty__(self, prop):
        # us.getHometown() should return InappropriatePropertyException
        # rome.getNominalGDP() should return MissingDataException
        raise InappropriatePropertyException(self, prop)

class EntityPropertyGetter:
    def __init__(self, entity, prop):
        self.entity = entity
        self.prop = prop

    def __call__(self):
        return self.entity.get(self.prop)


class Property:
    "Property representative"
    def __init__(self, knps, propertyUri, entityUri, accessorName):
        self.knps = knps
        self.propertyUri = propertyUri
        self.entityUri = entityUri
        self.accessorName = accessorName

        self.knps.registerProperty(self, accessorName)

        self.facts = None

    @classmethod
    def wikidataProperty(cls, knps, wikidataPropertyId, accessorName):
        return cls(knps,
                   WIKIDATA_PROPERTY_PREFIX % str(wikidataPropertyId),
                   WIKIDATA_ENTITY_PREFIX % str(wikidataPropertyId),
                   accessorName)

    def __populate__(self):
        self.facts = {}
        for prop, val in self.knps.gr.getLiteralFacts(self.entityUri):
            self.facts.setdefault(prop, []).append(val)

        for prop, val in self.knps.gr.getEntityFacts(self.entityUri):
            self.facts.setdefault(prop, []).append(val)
            
    def get(self, prop):
        if self.facts is None:
            self.__populate__()

        x = self.facts.get(prop.getPropertyUri())
        if len(x) == 1:
            return x[0]
        else:
            return x

    def getPropertyUri(self):
        return self.propertyUri

    def __str__(self):
        if self.facts is None:
            self.__populate__()
            
        return " ".join(self.facts.get(LABEL_PROPERTY))


class GraphRepo:
    "The backing graph service"
    def __init__(self, knps, serviceurl):
        self.knps = knps
        self.serviceurl = serviceurl


    def __eq__(self, other):
        return isinstance(other, GraphRepo) and self.serviceurl == other.serviceurl

    def getExamplesOfEntity(self, entityUri):
        q = """SELECT ?s
               WHERE {
               ?s <%s> <%s>
               }""" % (INSTANCE_OF_URI, entityUri)

        result = sparql.query(self.serviceurl, (q))

        for row in result:
            vals = sparql.unpack_row(row)
            v = vals[0]
            if v.find(WIKIDATA_ENTITY_PREFIX % "") == 0:
                v = Entity(self.knps, v)
            yield v

    def getLiteralFacts(self, entityUri):
        q = """SELECT ?p ?o
               WHERE {
               <%s> ?p ?o
               FILTER(isLiteral(?o))
               FILTER((!(isLiteral(?o) && strlen(lang(?o)) > 0)) || (lang(?o) = "en"))
               } """ % (entityUri)
        result = sparql.query(self.serviceurl, (q))

        for row in result:
            vals = sparql.unpack_row(row)
            yield vals[0], vals[1]

    def getEntityFacts(self, entityUri):
        q = """SELECT ?p ?o
               WHERE {
               <%s> ?p ?o
               FILTER(! isLiteral(?o))
               FILTER((!(isLiteral(?o) && strlen(lang(?o)) > 0)) || (lang(?o) = "en"))
               } """ % (entityUri)
        result = sparql.query(self.serviceurl, (q))

        for row in result:
            vals = sparql.unpack_row(row)
            v = vals[1]
            if v.find(WIKIDATA_ENTITY_PREFIX % "") == 0:
                v = Entity(self.knps, v)
            
            yield vals[0], v


    def close(self):
        pass
    
