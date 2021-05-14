
import xml.etree.ElementTree as ET #to parse xml
import os
import sys
import optparse
import random

# importing python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  
import traci  

def generate_report(filename):

    tree = ET.parse(filename) #read file
    root = tree.getroot() #get root
    sum_waitTime=0.0
    sum_timeloss=0.0
    count=0
    for child in root:
        count+=1;
        sum_waitTime+=float(child.attrib["waitingTime"])
        sum_timeloss+=float(child.attrib["timeLoss"])
        
    avg_waitTime=sum_waitTime/count #find average
    avg_timeloss=sum_timeloss/count

    print("Average Waiting Time:  "+str(avg_waitTime))
    print("Average Time Lost:  "+str(avg_timeloss))

def runC():
    step = 0
    ind=0
    time=42.0
    tlsIndex="gneJ1"
    
    traci.trafficlight.setPhase(tlsIndex,ind) #initial phase
    traci.trafficlight.setPhaseDuration(tlsIndex, time)

    ind=ind+1
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()#start simulation
        step=step+1
        if step==time+1:# if phase change
            if ind%2==0:#green phase
                time=42.0
                
                traci.trafficlight.setPhase(tlsIndex,ind)
                traci.trafficlight.setPhaseDuration(tlsIndex, time)
                
            else:#yellow phase
                time=3.0
                
                traci.trafficlight.setPhase(tlsIndex,ind)
                traci.trafficlight.setPhaseDuration(tlsIndex, time)
                
            print("step: "+str(step)+", phase: "+str(ind)+", time: "+str(time))
            step=0
            if ind==7:
                ind=0#go to first phase
            else:
                ind=ind+1#go to next phase
            

    traci.close()
    sys.stdout.flush()

def getTime(d):#set time
    if (d<3):
        return 10.0
    elif (d<6):
        return 20.0
    elif (d<9):
        return 30.0
    elif (d<12):
        return 35.0
    elif (d>12):
        return 42.0

def getCount(index):#get vehicle count
    count=0
    if index==0:
        ch="B"
    elif index==2:
        ch="C"
    elif index==4:
        ch="D"
    else:
        ch="A"
    
    for k in traci.lane.getLastStepVehicleIDs("r"+ch+"-incoming_0"):
        if traci.vehicle.getLanePosition(k) < 100:
            count += 1
    return count

def runP():
    """execute the TraCI control loop""" 
    step = 0
    ind=0
    time=42.0
    tlsIndex="gneJ1"
    
    traci.trafficlight.setPhase(tlsIndex,ind)
    traci.trafficlight.setPhaseDuration(tlsIndex, time)
    ind=ind+1
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step=step+1
        if step==time+1:
            if ind%2==0:#green phase
                count=getCount(ind)
                time=getTime(count)
                traci.trafficlight.setPhase(tlsIndex,ind)
                traci.trafficlight.setPhaseDuration(tlsIndex, time)
                
            else: #yello phase
                time=3.0
                traci.trafficlight.setPhase(tlsIndex,ind)
                traci.trafficlight.setPhaseDuration(tlsIndex, time)
                
            print("step: "+str(step)+", phase: "+str(ind)+", time: "+str(time))
            step=0
            if ind==7: #reach last phase
                ind=0 #then, go to first phase
            else: 
                ind=ind+1 #go to next phase
            

    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options



if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    #user selection
    print("Conventional method vs Proposed method") 
    print("Press C for Conventional method")
    print("Press P for Proposed method")
    s=input()
    
    

    # sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "traffic.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])

    if s=="C":
        runC()
    elif s=="P":
        runP()
    else:
        print("Invalid")
    #generate output report
    generate_report("tripinfo.xml")
    
    