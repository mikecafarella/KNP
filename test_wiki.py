import KGType
import kgpl
import KNPSStore
import time
import query
import wikidata_utils
import uuid

if __name__ == '__main__':
    val1 = kgpl.KGPLWiki("Q100000")
    val1.register("localhost")
    # id = uuid.uuid4()
    # print(type(id))
    # print(id)
    # val1 = kgpl.KGPLInt(42)
    # print(val1)
    # print(type(val1))
    # val1.register("localhost")
    # val2 = kgpl.KGPLInt(42)
    # val1 = kgpl.KGPLWiki("Q100000")
    # print(val1)
    # print("--------")
    # print(val1.properties)

    # val3 = {
    #     "py/object": "kgpl.kgpl.KGPLInt",
    #     "val": 42,
    # }
    # print(type(val3))

    # zjy_float = kgpl.KGPLValue(2.3)  # kgpl value
    # var7 = kgpl.KGPLVariable(zjy_float)  # kgpl variable
    # print(var7.__str__())
    # print(var7.__repr__())
    # print("---------")
    # var7.registerVariable()

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
    # # print(temp)
    # # print()
    # # print(temp.properties)
    # tempVariable = kgpl.KGPLVariable(kgpl.KGPLInt(1))
    # tempVariable.registerVariable()
    # tempVariable.reassign(temp)

    # print(type(temp2))
    # print()
    # print(type(temp2.currentvalue))
    # print()
    # print(temp2.currentvalue.name)
    # print()
    # print(temp2)

    # temp2 = kgpl.getVariable('K4')
    # print("Now (K4 val 1): " + str(type(temp2.currentvalue)))
    #
    # temp2.reassign(temp)
    # temp2 = kgpl.getVariable('K4')
    # print("Now (K4 val 2): " + str(type(temp2.currentvalue)))

    # zjy_float = kgpl.KGPLValue(2.3)  # kgpl value
    # var7 = kgpl.KGPLVariable(zjy_float)  # kgpl variable
    # print(var7.__str__())
    # print(var7.__repr__())
    # print("---------")
    # var7.registerVariable()
    #
    # print(var7.__str__())
    # print(var7.__repr__())

    # temp = kgpl.KGPLWiki("Q100000")
    # var8 = kgpl.KGPLVariable(temp)
    # print(var8.__str__())
    # print(var8.__repr__())
    # print("---------")
    #

    # print("+++++")
    # temp3 = kgpl.getVariable('K7')
    # print(temp3.__str__())
    # print("---")
    # print(temp3.__repr__())

    # temp = kgpl.KGPLWiki("Q100000")
    # print(temp.__repr__())
    # print("-------")
    # print(temp.__str__())
    #
    # print("++++++++")
    # temp2 = kgpl.getVariable('K9')
    # print(temp2.__repr__())
    # print("---")
    # print(temp2.__str__())
