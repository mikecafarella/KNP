import KGType
import kgpl
import KNPSStore
import time

def programA():
    currentTime = kgpl.KGPLFloat(time.time())
    timeThisProgramWasRun = kgpl.KGPLVariable(currentTime)
    timeThisProgramWasRun.registerVariable()
    return timeThisProgramWasRun.varName

def programB(temp):
    time.sleep(5)
    mikesProgramTime = kgpl.getVariable(temp)
    currentTime = kgpl.KGPLFloat(time.time())
    print("Difference between two programs:" + str(currentTime.val - mikesProgramTime.currentvalue.val))

if __name__ == '__main__':
    temp = programA()
    programB(temp)