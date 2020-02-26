#!/usr/bin/env python3
import yaml
import argparse
import os
import os.path
import pickle

import methods
from wikidata_utils import get_entity
from Levenshtein import distance

class KGPDir:
    def __init__(self, dir):
        self.dir = dir
        refinementsfile = os.path.join(self.dir, "refinements.yaml")
        with open(refinementsfile, "r") as fin:
            self.refinements = yaml.safe_load(fin)

        self.methods = set([methods.PlotTwoLines(),
                           methods.BasicLineChart(),
                           methods.OneNumericBoxPlot(),
                           methods.OneNumericBoxPlot(),
                           methods.OneNumericSeveralGroupBoxPlot(),
                           methods.BasicScatterPlot(),
                           methods.BasicHistogram(),
                           methods.AreaChart(),
                           methods.DensityPlot(),
                           methods.BubblePlot(),
                           methods.BasicViolinPlot(),
                           methods.PrintTexts(),
                           methods.TableGen()])

        self.invocations = self.refinements["invocations"]
                           
class Query:
    def __init__(self, fname):
        self.cacheName = "./.localKGCache"
        
        if os.path.exists(self.cacheName):
            with open(self.cacheName, "rb") as fin:
                self.kgcache = pickle.load(fin)
        else:
            self.kgcache = {}
            
        with open(fname, "r") as fin:
            querydesc = yaml.safe_load(fin)
            self.methodstring = querydesc["methodstring"]
            self.args = []
            self.arglabels = querydesc["args"]
            for x in querydesc["args"]:
                self.args.append(self.resolveKGReference(x))


    def resolveKGReference(self, referenceDesc):
        entityLabel = referenceDesc["entity"]
        propertyLabel = referenceDesc.get("property", None)

        if entityLabel in self.kgcache:
            return self.kgcache[entityLabel]
        else:
            resolvedEntity = get_entity(entityLabel)
            self.kgcache[entityLabel] = resolvedEntity
            with open(self.cacheName, "wb") as fout:
                pickle.dump(self.kgcache, fout)
            
            return resolvedEntity

    def isCorrectTargetMethod(self, candidateMethod):
        return 1 - distance(self.methodstring, type(candidateMethod).__name__)

    def isCorrectInvocation(self, candidateInvocation, candidateMethod):
        ################################################
        # Matching the query to the invocation
        ################################################
        #
        # Does the candidate Invocation's cardinality match the query?
        #
        candidateInvocationCard = candidateInvocation["params"]["cardinality"]
        cardinalityMatch = 0.05
        if candidateInvocationCard in ("zero", "lone"):
            if len(self.args) == 0:
                cardinalityMatch = 0.95
        elif candidateInvocationCard in ("zeroOrMore", "one", "oneOrMore", "lone"):
            if len(self.args) == 1:
                cardinalityMatch = 0.95
        elif candidateInvocationCard in ("zeroOrMore", "twoOrMore", "oneOrMore"):
            if len(self.args) >= 2:
                cardinalityMatch = 0.95
            
        #
        # Does the candidate's Invocation's type signature match the query's type signature?
        # In the future we should use a classifier to determine this question.
        # For now, let's use the Wikidata object's instance-of property.
        #
        argTypeMatch = 0
        if "type" in candidateInvocation["params"]:
            argTypes = []
            for arg in self.args:
                curArgType = set()
                typeProperty = "P31"
                for propertyRelevantClaim in arg["claims"][typeProperty]:
                    mainsnak = propertyRelevantClaim["mainsnak"]
                    datavalue = mainsnak["datavalue"]
                    if datavalue["type"] == "wikibase-entityid":
                        value = datavalue["value"]                    
                        instanceOfId = value["id"]
                        curArgType.add(instanceOfId)
                argTypes.append(curArgType)

                #
                # This will work for instance-of, but nothing else.
                # We really need a more systematic way of handling type membership.
                # Relying on instance-of is too brittle
                # 

            candidateInvocationType = candidateInvocation["params"]["type"]
            argTypeMatch = min([1 if candidateInvocationType in x else 0 for x in argTypes])

        ################################################
        # Matching the query to the target method
        ################################################
        # Does the method label match?
        methodLabelMatch = 1 - (distance(self.methodstring, type(candidateMethod).__name__) / float(max(len(self.methodstring), len(type(candidateMethod).__name__))))

        ################################################
        # Matching the invocation to the target method
        ################################################
        # Does the method type match?
        methodTypeMatch = 0
        if "method" in candidateInvocation:
            if candidateInvocation["method"]["type"] in candidateMethod.get_types():
                methodTypeMatch = 1


        #return cardinalityMatch + argTypeMatch + methodLabelMatch + methodTypeMatch
        return cardinalityMatch, argTypeMatch, methodTypeMatch        
        
def answerQuery(kgpdir, q):
    allMethodsAndInvocations = []
    for curMethod in kgpdir.methods:
        for curInvocation in kgpdir.invocations:
            #curMethodScore = q.isCorrectTargetMethod(curMethod)
            cardMatch, argTypeMatch, methodTypeMatch = q.isCorrectInvocation(curInvocation, curMethod)
            curInvocationScore = cardMatch + argTypeMatch + methodTypeMatch
            
            #print("Candidate invocatioN", curInvocation["name"], "candidate method", curMethod, curInvocationScore)
            allMethodsAndInvocations.append((curInvocationScore, (curInvocation, curMethod), (cardMatch, argTypeMatch, methodTypeMatch)))
            #curMappingScore = isCorrectMapping(curMethod, curMapping)

            #totalScore = isCorrectUserAnswer(curMethodScore, curInvocationScore, curMappingScore)
            #totalScore = isCorrectUserAnswer(curMethodScore, curInvocationScore)
            #candidateAnswers.append((totalScore, (curMethod, curInvocation, curMapping)))
            #candidateAnswers.append((totalScore, (curMethod, curInvocation)))

    allMethodsAndInvocations.sort(key=lambda x: x[0], reverse=True)
    print()
    print()
    print()
    print("Results for query", q.methodstring, q.arglabels)
    for score, invokeTuple, scoreDetails in allMethodsAndInvocations[0:]:
        curInvocation, curMethod = invokeTuple
        print(score, curMethod, curInvocation["name"], scoreDetails)
        print()
                


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Next-gen KNP type-driven query processing tool")

    parser.add_argument("--kgpdir", help="Which KGP directory to look at")
    parser.add_argument("--query", help="Query YAML to execute")

    args = parser.parse_args()

    if args.kgpdir and args.query:
        kgpdir = KGPDir(args.kgpdir)
        query = Query(args.query)

        answerQuery(kgpdir, query)
        
                
    

