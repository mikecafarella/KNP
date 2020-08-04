#!/usr/bin/env python
import sparql
import inspect
import uuid
from abc import ABC, abstractmethod
import requests
import pickle, codecs

WIKIDATA_ENTITY_PREFIX = "http://www.wikidata.org/entity/%s"
WIKIDATA_STATEMENT_PREFIX = "http://www.wikidata.org/entity/statement/%s"
WIKIDATA_PROPERTY_PREFIX = "http://www.wikidata.org/prop/%s"

WIKIDATA_PROPERTY_STATEMENT_PREFIX = "http://www.wikidata.org/prop/statement/%s"
WIKIDATA_PROPERTY_QUALIFIER_PREFIX = "http://www.wikidata.org/prop/qualifier/%s"

RDF_TYPE_PROPERTY_URI = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
BESTRANK_URI = "http://wikiba.se/ontology#BestRank"

INSTANCE_OF_URIS = ["http://www.wikidata.org/prop/direct/P31"]
TYPICAL_PROPERTIES_URIS = ["http://www.wikidata.org/prop/P1963"]

LABEL_PROPERTY = "http://www.w3.org/2000/01/rdf-schema#label"
IMAGE_PROPERTY = "http://www.wikidata.org/prop/direct/P18"

KGPL_SRC_CODE_PROPERTY_URI = "http://kgpl.org/prop/P1"
KGPL_PICKLED_CODE_PROPERTY_URI = "http://kgpl.org/prop/P2"


def isEntityUri(uri):
    return isinstance(uri, str) and uri.find(WIKIDATA_ENTITY_PREFIX % "") == 0

def isStatementUri(uri):
    return isinstance(uri, str) and uri.find(WIKIDATA_STATEMENT_PREFIX % "") == 0

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
        self.facts = None

    @property
    def entityUri(self):
        return self._entityUri

    @classmethod    
    def entityFromURI(cls, knps, entityUri):
        if isStatementUri(entityUri):
            raise Exception("URI describes a Statement Item, not an Entity " + str(entityUri))
        
        if entityUri in Entity.knownEntities:
            return Entity.knownEntities[entityUri]
        else:
            newEntity = cls(knps, entityUri)
            Entity.knownEntities[entityUri] = newEntity
            return newEntity

    def startPopulate(self):
        if self.facts is None:
            self.facts = {}
        
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
        #for prop, val in self.knps.gr.getEntityFacts(self.entityUri):
        #    self.facts.setdefault(prop.propertyUri, []).append(val)
        for prop, val in self.knps.gr.getEntityStatementFacts(self.entityUri):
            self.facts.setdefault(prop.propertyUri, []).append(val)

        for prop, val in self.knps.gr.getEntityNonstatementFacts(self.entityUri):
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
    def __get(self, prop, ignoreNone=False):
        if self.facts is None:
            self.__populate__()

        x = self.facts.get(prop.propertyUri)
        if x is None and not ignoreNone:
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

    def getBestSingleton(self, prop, ignoreNone=False):
        b = self.getBest(prop, ignoreNone=ignoreNone)
        if b is not None:
            return b[0]
        else:
            return b

    def getBest(self, prop, ignoreNone=False):
        "Get best tuples, with simple property value"
        x = self.__get(prop, ignoreNone=ignoreNone)

        if x is None:
            return x

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

        @classmethod
        def getExamples(cls):
            return cls.entity.knps.gr.getExamplesOfEntity(cls.entity.entityUri)

        @classmethod
        def getTypicalProperties(cls):
            result = []
            for typicalPropertiesProperty in cls.typicalPropertiesProperties:
                result.extend(cls.entity.get(typicalPropertiesProperty))
            return result

        @classmethod
        def __instancecheck__(cls, instance):
            for instanceProperty in cls.instanceProperties:
                if cls.entity.get(instanceProperty) == instance:
                    return True
            return False
        
        clsAttrs = {"entity": self,
                    "typicalPropertiesProperties": [Property.propertyFromURI(self.knps, x) for x in TYPICAL_PROPERTIES_URIS],
                    "instanceProperties": [Property.propertyFromURI(self.knps, x) for x in INSTANCE_OF_URIS],
                    "getExamples": getExamples,
                    "__instancecheck__": __instancecheck__,
                    "getTypicalProperties": getTypicalProperties}
        
        newCls = type(clsName, clsBases, clsAttrs)
        return newCls

    def label(self):
        if self.facts is None:
            self.__populate__()

        return " ".join(self.facts.get(LABEL_PROPERTY, []))

    def imageUrl(self):
        if self.facts is None:
            self.__populate__()

        imgUrls = self.facts.get(IMAGE_PROPERTY, [])
        if len(imgUrls) == 0:
            return None
        else:
            return imgUrls[0]

    def __str__(self):
        return self.entityUri + " (" + self.label() + ")"
    
    def __repr__(self):
        return self.__str__()

    def _repr_html_(self):
        members = [self.entityUri, self.label()]
        htmlStr = "<tr><td>" + "</td><td>".join(members) + "</td>"
        if self.imageUrl() is not None:
            htmlStr += f'<td><img width=100 src="{self.imageUrl()}">'
        htmlStr += "</td></tr>"
        return htmlStr 

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
        rdfTypeProperty = Property.propertyFromURI(self.knps, RDF_TYPE_PROPERTY_URI)
        for rdfTypeVal in self.get(rdfTypeProperty):
            if rdfTypeVal.find(BESTRANK_URI) == 0:
                return True
        return False


class KGPLFunction:
    def __init__(self, knps, userfunc, uri):
        self.knps = knps
        self.userfunc = userfunc
        self.uri = uri
        self.facts = {}

        if self.userfunc is None:
            self.__populate__()

    def __populate__(self):
        for prop, val in self.knps.gr.getLiteralFacts(self.uri):
            self.facts.setdefault(prop.propertyUri, []).append(val)
            
        for prop, val in self.knps.gr.getEntityFacts(self.uri):
            self.facts.setdefault(prop.propertyUri, []).append(val)

        pickledCodeProperty = Property.propertyFromURI(self.knps, KGPL_PICKLED_CODE_PROPERTY_URI)

        pickledStr = self.facts.get(pickledCodeProperty.propertyUri)[0]
        self.userfunc = pickle.loads(codecs.decode(pickledStr.encode(), "base64"))

    def store(self):
        srcCodeProperty = Property.propertyFromURI(self.knps, KGPL_SRC_CODE_PROPERTY_URI)
        pickledCodeProperty = Property.propertyFromURI(self.knps, KGPL_PICKLED_CODE_PROPERTY_URI)
        #self.knps.gr.storeFact(self.uri, srcCodeProperty.propertyUri, inspect.getsource(self.userfunc))
        
        pickledStr = codecs.encode(pickle.dumps(self.userfunc), "base64").decode()
        self.knps.gr.storeFact(self.uri, pickledCodeProperty, pickledStr)
        
        self.__populate__()

    def __call__(self, arg):
        return self.userfunc(arg)

    @property
    def funcname(self):
        return self.userfunc.__name__

    @classmethod
    def fetchFunction(cls, knps, uri):
        return cls(knps, None, uri)

    @classmethod
    def registerFunction(cls, knps, userfunc, uri):
        kf = cls(knps, userfunc, uri)
        kf.store()

        return kf

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
    def propertyFromURI(cls, knps, propertyUri, accessorName=None):
        if propertyUri in Property.knownProperties:
            return Property.knownProperties[propertyUri]
        else:
            if propertyUri.find(WIKIDATA_PROPERTY_PREFIX%"") == 0:
                entityUri = WIKIDATA_ENTITY_PREFIX % propertyUri[len(WIKIDATA_PROPERTY_PREFIX%""):]
            else:
                entityUri = None
                
            newProp = cls(knps,
                          propertyUri,
                          entityUri)
            
            Property.knownProperties[propertyUri] = newProp

            if accessorName is not None:
                knps.registerProperty(newProp, accessorName)
            
            return newProp

    def getEntitiesWithThisProperty(self):
        return self.knps.gr.getExamplesOfEntitiesWithProperty(self.propertyUri)

    def __populate__(self):
        self.facts = {}

        if self.entityUri is not None:
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

    def label(self):
        if self.facts is None:
            self.__populate__()

        return " ".join(self.facts.get(LABEL_PROPERTY, []))
            
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

    def storeFact(self, s, p, o):
        q = """INSERT DATA
               {
                 <%s> <%s> '''%s'''
               }""" % (str(s), str(p), str(o))
        storeURI = self.serviceurl + "/statements"
        r = requests.post(url=storeURI, params={
            "update":q
            })

        if r.status_code == 200 or r.status_code == 204:
            return True
        else:
            raise Exception("INSERT HTTP status error: " + str(r.status_code))

    def findEntityViaText(self, strs):
        q = """SELECT ?s
        WHERE {
        }""" % ()

    def getExamplesOfEntity(self, entityUri):
        q = """SELECT ?s
               WHERE {
               ?s <%s> <%s>
               }""" % (INSTANCE_OF_URIS[0], entityUri)

        result = sparql.query(self.serviceurl, (q))

        for row in result:
            vals = sparql.unpack_row(row)
            v = vals[0]
            if isEntityUri(v):
                v = Entity(self.knps, v)
            yield v

    def getExamplesOfEntitiesWithProperty(self, propertyUri):
        q = """SELECT ?s
               WHERE {
               ?s <%s> ?o
               }""" % (propertyUri)

        result = sparql.query(self.serviceurl, (q))

        for row in result:
            vals = sparql.unpack_row(row)
            v = vals[0]
            if isEntityUri(v):
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
            p = Property.propertyFromURI(self.knps, p)
            
            yield p, vals[1]

    def getEntityStatementFacts(self, entityUri):
        q = """SELECT ?p ?o ?p2 ?o2
               WHERE {
               <%s> ?p ?o
               FILTER(! isLiteral(?o))
               FILTER regex(str(?o), "^http://www.wikidata.org/entity/statement/")
               FILTER((!(isLiteral(?o) && strlen(lang(?o)) > 0)) || (lang(?o) = "en")).
               ?o ?p2 ?o2
               } """ % (entityUri)
        result = sparql.query(self.serviceurl, (q))

        seen = set()
        for row in result:
            vals = sparql.unpack_row(row)
            p = vals[0]
            v = vals[1]
            key = p + "_" + v
            
            p = Property.propertyFromURI(self.knps, p)

            if isStatementUri(v):
                v = Statement.statementFromURI(self.knps, v)
            elif isEntityUri(v):
                v = Entity.entityFromURI(self.knps, v)

            p2 = vals[2]
            p2 = Property.propertyFromURI(self.knps, p2)
            v2 = vals[3]
            if isStatementUri(v2):
                v2 = Statement.statementFromURI(self.knps, v2)
            elif isEntityUri(v2):
                v2 = Entity.entityFromURI(self.knps, v2)

            v.startPopulate()
            v.facts.setdefault(p2.propertyUri, []).append(v2)

            if key in seen:
                continue
            else:
                seen.add(key)
                yield p, v


    def getEntityNonstatementFacts(self, entityUri):
        q = """SELECT ?p ?o
               WHERE {
               <%s> ?p ?o
               FILTER(! isLiteral(?o))
               FILTER regex(str(?o), "^((?!statement).)*")
               FILTER((!(isLiteral(?o) && strlen(lang(?o)) > 0)) || (lang(?o) = "en"))
               } """ % (entityUri)
        result = sparql.query(self.serviceurl, (q))
        
        for row in result:
            vals = sparql.unpack_row(row)
            p = vals[0]
            v = vals[1]

            p = Property.propertyFromURI(self.knps, p)

            if isStatementUri(v):
                v = Statement.statementFromURI(self.knps, v)
            elif isEntityUri(v):
                v = Entity.entityFromURI(self.knps, v)
            
            yield p, v

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

            p = Property.propertyFromURI(self.knps, p)

            if isStatementUri(v):
                v = Statement.statementFromURI(self.knps, v)
            elif isEntityUri(v):
                v = Entity.entityFromURI(self.knps, v)
            
            yield p, v


    def close(self):
        pass
    
