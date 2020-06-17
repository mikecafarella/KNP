import kgpl


if __name__ == '__main__':

    temp1 = kgpl.KGPLWiki("Q100008")
    tempVariable = kgpl.KGPLVariable(temp1)
    tempVariable.registerVariable()
    print(tempVariable.varName)
    temp2 = kgpl.getVariable("Q100008")
    temp2.viewHistory()
