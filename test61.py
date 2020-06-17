import kgpl
import time
import query
import wikidata_utils
import json


if __name__ == '__main__':
    temp1 = kgpl.KGPLInt(1)
    temp2 = kgpl.KGPLStr("skr")
    temp3 = kgpl.KGPLFloat(3.14)
    tempList = [1, 2, 3, 4]
    temp4 = kgpl.KGPLList(tempList)
    tempTuple = (7, 8, 9)
    temp5 = kgpl.KGPLTuple(tempTuple)
    tempDict = {
                "key1": "value1",
                23: 3.45
                }
    temp6 = kgpl.KGPLDict(tempDict)
    tempVariable = kgpl.KGPLVariable(temp1)
    tempVariable.registerVariable()
    print(tempVariable.varName)
    tempName = tempVariable.varName
    tempVariable.reassign(temp2)
    tempVariable.reassign(temp3)
    tempVariable.reassign(temp4)
    tempVariable.reassign(temp5)
    tempVariable.reassign(temp6)
    tempVariable = kgpl.getVariable(tempName)
    tempVariable.viewHistory()