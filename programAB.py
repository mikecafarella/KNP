import KGType
import kgpl
import KNPSStore
import time

def programA():
    currentTime = kgpl.KGPLFloat(time.time())
    timeThisProgramWasRun = kgpl.KGPLVariable(kgpl.KGPLInt(1))
    timeThisProgramWasRun.registerVariable()
    timeThisProgramWasRun.reassign(currentTime)
    print(kgpl.getVariable(timeThisProgramWasRun.varName))
    return timeThisProgramWasRun.varName

def programB(temp):
    mikesProgramTime = kgpl.getVariable(temp)
    currentTime = kgpl.KGPLFloat(time.time())
    print("Difference between two programs:" + str(currentTime.val - mikesProgramTime.currentvalue.val))

if __name__ == '__main__':
    temp = programA()
    print(temp)
    time.sleep(5)
    programB(temp)
    # temp = kgpl.getVariable('K14')
    # print('okok')
    # temp.viewHistory()