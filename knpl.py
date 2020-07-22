#!/usr/bin/env python
import sparql
from abc import ABC, abstractmethod

WIKIDATA_ENTITY_PREFIX = "http://www.wikidata.org/entity/%s"
WIKIDATA_STATEMENT_PREFIX = "http://www.wikidata.org/entity/statement/%s"

WIKIDATA_PROPERTY_PREFIX = "http://www.wikidata.org/prop/%s"
WIKIDATA_PROPERTY_STATEMENT_PREFIX = "http://www.wikidata.org/prop/statement/%s"
WIKIDATA_PROPERTY_QUALIFIER_PREFIX = "http://www.wikidata.org/prop/qualifier/%s"

RDF_TYPE_PROPERTY_URI = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
BESTRANK_URI = "http://wikiba.se/ontology#BestRank"

INSTANCE_OF_URI = "http://www.wikidata.org/prop/direct/P31"

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
    knownEntities = {}
    
    def __init__(self, knps, entityUri):
        self.knps = knps
        self._entityUri = entityUri

        if not entityUri.find(WIKIDATA_ENTITY_PREFIX % "") == 0:
            raise Exception("URI does not describe an Entity " + str(entityUri))
        
        self.facts = None

    @property
    def entityUri(self):
        return self._entityUri

    @classmethod
    def wikidataEntity(cls, knps, wikidataId):
        entityUri = WIKIDATA_ENTITY_PREFIX % str(wikidataId)        
        return Entity.wikidataEntityFromURI(knps, entityUri)

    @classmethod    
    def wikidataEntityFromURI(cls, knps, entityUri):
        if entityUri.find(WIKIDATA_STATEMENT_PREFIX % "") == 0:
            raise Exception("URI describes a Statement Item, not an Entity " + str(entityUri))
        
        if entityUri in Entity.knownEntities:
            return Entity.knownEntities[entityUri]
        else:
            newEntity = cls(knps, entityUri)
            Entity.knownEntities[entityUri] = newEntity
            return newEntity

    def __populate__(self):
        self.facts = {}

        for prop, val in self.knps.gr.getLiteralFacts(self.entityUri):
            self.facts.setdefault(prop.propertyUri, []).append(val)

        #
        # Consider
        # http://www.wikidata.org/prop/P1082
        # VS
        # http://www.wikidata.org/prop/direct/P1082
        #
        # The "direct" element seems to do a few different things:
        # 1) It automatically removes the "Statement" object wrapper and
        #    returns a single value
        # 2) If the data is multivalued and some elements are marked as 'bestRank'
        #    or 'preferredRank', then ONLY that set of elements will be returned.
        #    (If there is no possible ranking, then /direct/ will return the entire
        #    set.)
        #
        # This means that `direct` might be handy, but cannot be used to grab entire
        # datasets. Moreover, it might be doing other magic that we can't see.
        #
        #
        for prop, val in self.knps.gr.getEntityFacts(self.entityUri):
            self.facts.setdefault(prop.propertyUri, []).append(val)

    def __eq__(self, other):
        return self.entityUri == other.entityUri

    def __hash__(self):
        return hash(self.entityUri)

    #
    # TODO: better get()ting.
    #
    # A single get() method is too restrictive.
    #
    # We need a full complement of get() methods that can:
    # a) get(): Return the full set of simple values
    # b) getRelation(): Return the full relation (that is, non-simple values) 
    # c) getBest(): Return the "best" simple value(s)
    # d) getBestRelation(): Return the "best" full relation (non-simple values)
    #
    #
    def __get(self, prop):
        if self.facts is None:
            self.__populate__()

        x = self.facts.get(prop.propertyUri)
        if x is None:
            self.__handleMissingProperty__(prop)

        return x

    def get(self, prop):
        "Get all tuples, with simple property value"
        x = self.__get(prop)
        
        #
        # Is this in direct mode or not? I think we should do NOT direct mode
        #
        if len(x) == 1:
            stmt = x[0]
            return stmt.get(prop)
        else:
            return [stmt.get(prop) for stmt in x]

    def getRelation(self, prop):
        "Get all tuples, with all properties"
        x = self.__get(prop)

        if len(x) == 1:
            return x[0]
        else:
            return x

    def getBest(self, prop):
        "Get best tuples, with simple property value"
        x = self.__get(prop)

        if len(x) == 1:
            stmt = x[0]
            return stmt.get(prop)
        else:
            # find the stmts that are best
            bestStmts = [stmt for stmt in x if stmt.hasBestRankFact()]
            if len(bestStmts) > 0:
                return [stmt.get(prop) for stmt in bestStmts]
            else:
                return [stmt.get(prop) for stmt in x]
                
        
    def getBestRelation(self, prop):
        "Get all tuples, with all properties"
        x = self.__get(prop)
        if len(x) == 1:
            return x[0]
        else:
            # find the stmts that are best
            bestStmts = [stmt for stmt in x if stmt.hasBestRankFact()]
            if len(bestStmts) > 0:
                return bestStmts
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

        return " ".join(self.facts.get(LABEL_PROPERTY, []))

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

#
#
#
class Statement(Entity):
    "Statement representative"
    knownStatements = {}
    
    @classmethod
    def statementFromURI(cls, knps, entityUri):
        if entityUri in Statement.knownStatements:
            return Statement.knownStatements[entityUri]
        else:
            newStmt = cls(knps, entityUri)
            Statement.knownStatements[entityUri] = newStmt
            return newStmt

    def __init__(self, knps, stmtUri):
        super().__init__(knps, stmtUri)

    def __str__(self):
        if self.facts is None:
            self.__populate__()

        return "Statement(Fact):" + self.entityUri


    def get(self, prop):
        if self.facts is None:
            self.__populate__()

        if not prop.isWikidataProperty():
            return self.facts.get(prop.propertyUri)
        else:
            if prop.uriAsStatementUri() in self.facts:
                return self.facts.get(prop.uriAsStatementUri())[0]
            elif prop.uriAsQualifierUri() in self.facts:
                return self.facts.get(prop.uriAsQualifierUri())[0]
            else:
                #raise Exception("Cannot find property " + str(prop) + " in Statement " + str(self))
                return None


    def hasBestRankFact(self):
        rdfTypeProperty = Property.wikidataPropertyFromURI(self.knps, RDF_TYPE_PROPERTY_URI)
        for rdfTypeVal in self.get(rdfTypeProperty):
            if rdfTypeVal.find(BESTRANK_URI) == 0:
                return True
        return False
        

class EntityPropertyGetter:
    def __init__(self, entity, prop):
        self.entity = entity
        self.prop = prop

    def __call__(self):
        return self.entity.get(self.prop)


class Property:
    "Property representative"
    knownProperties = {}
    
    def __init__(self, knps, propertyUri, entityUri):
        self.knps = knps
        self._propertyUri = propertyUri
        self.entityUri = entityUri
        self.facts = None

    @property
    def propertyUri(self):
        return self._propertyUri

    def uriAsStatementUri(self):
        suffix = self.propertyUri[len(WIKIDATA_PROPERTY_PREFIX%""):]
        return WIKIDATA_PROPERTY_STATEMENT_PREFIX % suffix

    def uriAsQualifierUri(self):
        suffix = self.propertyUri[len(WIKIDATA_PROPERTY_PREFIX%""):]
        return WIKIDATA_PROPERTY_QUALIFIER_PREFIX % suffix

    def isWikidataProperty(self):
        return self.propertyUri.find(WIKIDATA_PROPERTY_PREFIX%"") == 0

    @classmethod
    def wikidataProperty(cls, knps, wikidataPropertyId, an=None):
        propertyUri = WIKIDATA_PROPERTY_PREFIX % str(wikidataPropertyId)
        return Property.wikidataPropertyFromURI(knps, propertyUri, accessorName=an)

    @classmethod
    def wikidataPropertyFromURI(cls, knps, propertyUri, accessorName=None):
        wikidataIdentifier = propertyUri[len(WIKIDATA_PROPERTY_PREFIX % ""):]
        entityUri = WIKIDATA_ENTITY_PREFIX % str(wikidataIdentifier)
        
        if propertyUri in Property.knownProperties:
            return Property.knownProperties[propertyUri]
        else:
            newProp = cls(knps,
                          propertyUri,
                          entityUri)
            
            Property.knownProperties[propertyUri] = newProp

            if accessorName is not None:
                knps.registerProperty(newProp, accessorName)
            
            return newProp

    def __populate__(self):
        self.facts = {}

        for prop, val in self.knps.gr.getLiteralFacts(self.entityUri):
            self.facts.setdefault(prop.propertyUri, []).append(val)

        for prop, val in self.knps.gr.getEntityFacts(self.entityUri):
            self.facts.setdefault(prop.propertyUri, []).append(val)
            
    def get(self, prop):
        if self.facts is None:
            self.__populate__()

        #
        # These should all be Statements
        #
        x = self.facts.get(prop.propertyUri)
        if len(x) == 1:
            stmt = x[0]
            return stmt
        else:
            return x

    def __eq__(self, other):
        return isinstance(self, Property) and isinstance(other, Property) and self.propertyUri == other.propertyUri

    def __hash__(self):
        return hash(self.propertyUri)
            
    def __str__(self):
        if self.facts is None:
            self.__populate__()
            
        return self.propertyUri


class GraphRepo:
    "The backing graph service"
    def __init__(self, knps, serviceurl):
        self.knps = knps
        self.serviceurl = serviceurl
        self.propertyCache = {}


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
            p = vals[0]
            p = Property.wikidataPropertyFromURI(self.knps, p)
            
            yield p, vals[1]

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
            p = vals[0]
            v = vals[1]

            p = Property.wikidataPropertyFromURI(self.knps, p)

            if v.find(WIKIDATA_STATEMENT_PREFIX % "") == 0:
                v = Statement.statementFromURI(self.knps, v)
            elif v.find(WIKIDATA_ENTITY_PREFIX % "") == 0:
                v = Entity.wikidataEntityFromURI(self.knps, v)
            
            yield p, v


    def close(self):
        pass
    
