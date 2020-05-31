import KGType
import kgpl
import KNPSStore
import time
import query
import wikidata_utils



if __name__ == '__main__':
    # temp = query.IR('Q76', 'wikidata', 'P69')
    # print(temp)
    # print(temp.properties)
    # temp2 = query.IR('Q76', 'wikidata')
    # print(temp2.properties)
    # wikidata_utils.get_entity('Q76')
    # temp = query.IR('Q76','wikidata')
    # print(temp.properties)
    # temp2 = query.IR('P22', 'wikidata')
    # print(temp2.properties)
    temp = kgpl.KGPLWiki("Q76")
    # print(temp)
    # print()
    # print(temp.properties)
    tempVariable = kgpl.KGPLVariable(kgpl.KGPLInt(1))
    tempVariable.registerVariable()
    tempVariable.reassign(temp)
    temp2 = kgpl.getVariable('K4')
    print(temp2)
