import matplotlib.pyplot as plt
import numpy as np
import math
import random
import statistics
from simulation import Simulator

from builder import generateFileIDs, MAX

def drawGraph(nodes, tasks):
    xs = []
    ys = [] 
    fx = []
    fy = []
    for _ in range(nodes):
        n = next(generateFileIDs())
        x = math.sin(2*math.pi*n/ MAX)
        y = math.cos(2*math.pi*n/ MAX)
        xs.append(x)
        ys.append(y)
    
    for _ in range(tasks):
        n = next(generateFileIDs())
        x = math.sin(2*math.pi*n/ MAX)
        y = math.cos(2*math.pi*n/ MAX)
        fx.append(x)
        fy.append(y)
    #plt.axes([-1.0,1.0,-1.0,1.0] )
    plt.plot(xs,ys, 'ro')
    plt.plot(fx,fy, 'b+')
    plt.show()
    
def drawEvenGraph(nodes, tasks):
    xs = []
    ys = [] 
    fx = []
    fy = []
    i = 0
    for _ in range(nodes):
        n = next(generateFileIDs())
        n = i/nodes * MAX
        x = math.sin(2*math.pi*n/ MAX)
        y = math.cos(2*math.pi*n/ MAX)
        xs.append(x)
        ys.append(y)
        i += 1
    
    for _ in range(tasks):
        n = next(generateFileIDs())
        x = math.sin(2*math.pi*n/ MAX)
        y = math.cos(2*math.pi*n/ MAX)
        fx.append(x)
        fy.append(y)
    #plt.axes([-1.0,1.0,-1.0,1.0] )
    plt.plot(xs,ys, 'ro')
    plt.plot(fx,fy, 'b+')
    plt.show()


def drawAverageChurn(filename):
    data =  open("data/done/"+filename+".txt")
    results = []
    current = {}
    
    for line in data:
        line = line.split() 
        churnRate =  float(line[5])
        work =  float(line[-2])
        slownessFactor =  float(line[13])
        if churnRate == 0:
            current = {}
            current["homogeneity"] = line[1]
            current["workMeasurement"] = line[2]
            current["rates"] = []
            current["times"] = []
            current["work"] =  []
            results.append(current)
        current["rates"].append(churnRate)
        current["times"].append(slownessFactor)
        current["work"].append(work)
    for result in results:
        print(result["times"][0])
        plt.plot(result["rates"], result["times"], "o-")
        plt.xlabel("Churn Per Tick")
        plt.ylabel("Runtime") 
        plt.ylim(1,8)
        plt.xlim(0,0.1)  
        plt.show()    
        
        plt.plot(result["rates"], result["work"], "o-")
        plt.xlabel("Churn Per Tick")
        plt.ylabel("Avg Work Per Tick")
        plt.xlim(0,0.1)  
        plt.show()


def drawRandomInjection(filename):
    data =  open("data/done/"+filename+".txt")
    results = []
    current = {}
    
    for line in data:
        line = line.split() 
        churnRate =  float(line[5])
        slownessFactor =  float(line[13])
        if churnRate == 0:
            current = {}
            current["homogeneity"] = line[1]
            current["workMeasurement"] = line[2]
            current["rates"] = []
            current["times"] = []
            results.append(current)
        current["rates"].append(churnRate)
        current["times"].append(slownessFactor)
    for result in results:
        print(result["times"][0])
        plt.plot(result["rates"], result["times"], "o")
    plt.show()    

def testInjectionSteps():
    s =  Simulator()
    s.setupSimulation(strategy = 'randomInjections',workMeasurement="one", numNodes=1000, numTasks=100000)
    loads, medians, means, maxs, devs = s.simulateLoad()
    for i in range(0,len(loads), 5):
        x = loads[i]
        plt.hist(x, 100, normed =1 )
        plt.xlabel('Tasks Per Node')
        plt.ylabel('Probability')
        plt.axvline(medians[i], color='r', linestyle='--')
        plt.axvline(means[i], color='k', linestyle='--')
        #plt.ylim(0, 0.05)
        plt.show()


def compareChurnInjection():
    s =  Simulator()
    random.seed(125)
    s.setupSimulation(strategy= "churn",  workMeasurement= "one", numNodes= 1000, numTasks = 100000, churnRate =0.01)
    loads1, medians1, means1, maxs1, devs1 = s.simulateLoad()
    random.seed(125)
    s=Simulator()
    s.setupSimulation(strategy = 'randomInjection',workMeasurement="one", numNodes=1000, numTasks=100000, churnRate=0)    
    loads2 = s.simulateLoad()[0]
    for i in range(0,len(loads1), 5):
        x1= loads1[i]
        x2 =loads2[i]
        colors = ["r", "b"]
        labels = ["Churn","Random Injection"]
        plt.hist([x1,x2], 25, normed =1, color=colors, label=labels)
        
        plt.legend(loc=0)
        plt.title('Churn vs Random Injection at Tick ' + str(i))

        plt.xlabel('Tasks Per Node')
        plt.ylabel('Fraction of the Network')
        #plt.ylim(0, 0.05)
        plt.show()
        
def compareChurnStable():
    s =  Simulator()
    random.seed(125)
    s.setupSimulation(strategy= "churn",  workMeasurement= "one", numNodes= 1000, numTasks = 100000, churnRate =0)
    loads1, medians1, means1, maxs1, devs1 = s.simulateLoad()
    random.seed(125)
    s=Simulator()
    s.setupSimulation(strategy= "churn",  workMeasurement= "one", numNodes= 1000, numTasks = 100000, churnRate =0.1)
    loads2 = s.simulateLoad()[0]
    for i in range(0,len(loads1), 5):
        x1= loads1[i]
        x2 =loads2[i]
        colors = ["k", "w"]
        labels = ["No Strategy","Churn"]
        plt.hist([x1,x2], 25, normed =1, color=colors, label=labels)
        
        plt.legend(loc=0)
        plt.title('Churn vs No Strategy at Tick ' + str(i))
        
        plt.xlabel('Tasks Per Node')
        plt.ylabel('Fraction of the Network')
        #plt.ylim(0, 0.05)
        plt.show()

def compareInjectionStable():
    s =  Simulator()
    random.seed(125)
    s.setupSimulation(strategy= "churn", homogeneity="equal" , workMeasurement= "one", numNodes= 1000, numTasks = 100000, churnRate =0)
    loads1, medians1, means1, maxs1, devs1 = s.simulateLoad()
    random.seed(125)
    s=Simulator()
    s.setupSimulation(strategy= "randomInjection", homogeneity="perStrength",  workMeasurement= "one", numNodes= 1000, numTasks = 100000, churnRate =0)
    loads2 = s.simulateLoad()[0]
    for i in range(0,len(loads1), 5):
        x1= loads1[i]
        x2 =loads2[i]
        colors = ["k", "w"]
        labels = ["No Strategy","Random Injection"]
        plt.hist([x1,x2], 25, normed =1, color=colors, label=labels)
        
        plt.legend(loc=0)
        plt.title('Random Injection in a Heterogeneous Network at Tick ' + str(i))
        
        
        plt.xlabel('Tasks Per Node')
        plt.ylabel('Fraction of the Network')
        #plt.ylim(0, 0.05)
        plt.show()
        
        
def compareNeighborsStable():
    s =  Simulator()
    random.seed(125)
    s.setupSimulation(strategy= "churn",  workMeasurement= "one", numNodes= 1000, numTasks = 100000, churnRate =0)
    loads1, medians1, means1, maxs1, devs1 = s.simulateLoad()
    random.seed(125)
    s=Simulator()
    s.setupSimulation(strategy= "neighbors",  workMeasurement= "one", numNodes= 1000, numTasks = 100000, churnRate =0)
    loads2 = s.simulateLoad()[0]
    for i in range(0,len(loads1), 5):
        x1= loads1[i]
        x2 =loads2[i]
        colors = ["k", "w"]
        labels = ["No Strategy","Neighbors"]
        plt.hist([x1,x2], 25, normed =1, color=colors, label=labels)
        
        plt.legend(loc=0)
        plt.title('Neighbors vs No Strategy at Tick ' + str(i))
        
        
        plt.xlabel('Tasks Per Node')
        plt.ylabel('Fraction of the Network')
        #plt.ylim(0, 0.05)
        plt.show()


def compareInviteStable():
    s =  Simulator()
    random.seed(125)
    s.setupSimulation(strategy= "churn",  workMeasurement= "one", numNodes= 1000, numTasks = 100000, churnRate =0)
    loads1, medians1, means1, maxs1, devs1 = s.simulateLoad()
    random.seed(125)
    s=Simulator()
    s.setupSimulation(strategy= "invite",  workMeasurement= "one", numNodes= 1000, numTasks = 100000, churnRate =0)
    loads2 = s.simulateLoad()[0]
    for i in range(0,len(loads1), 5):
        x1= loads1[i]
        x2 =loads2[i]
        colors = ["k", "w"]
        labels = ["No Strategy","Invitation"]
        plt.hist([x1,x2], 25, normed =1, color=colors, label=labels)
        
        plt.legend(loc=0)
        plt.title('Invitation vs No Strategy at Tick ' + str(i))
        
        
        plt.xlabel('Tasks Per Node')
        plt.ylabel('Fraction of the Network')
        #plt.ylim(0, 0.05)
        plt.show()
    
def compareInviteNeighbor():
    s =  Simulator()
    random.seed(125)
    s.setupSimulation(strategy= "neighbors",  workMeasurement= "one", numNodes= 1000, numTasks = 100000, churnRate =0)
    loads1, medians1, means1, maxs1, devs1 = s.simulateLoad()
    random.seed(125)
    s=Simulator()
    s.setupSimulation(strategy= "invite",  workMeasurement= "one", numNodes= 1000, numTasks = 100000, churnRate =0)
    loads2 = s.simulateLoad()[0]
    for i in range(0,len(loads1), 5):
        x1= loads1[i]
        x2 =loads2[i]
        colors = ["k", "w"]
        labels = ["Neighbors","Invitation"]
        plt.hist([x1,x2], 25, normed =1, color=colors, label=labels)
        
        plt.legend(loc=0)
        plt.title('Invitation vs Smart Neighbors at Tick ' + str(i))
        
        
        plt.xlabel('Tasks Per Node')
        plt.ylabel('Fraction of the Network')
        #plt.ylim(0, 0.05)
        plt.show()


def printTimeDiffs(fileA,fileB):
    naiveData = open("data/done/"+fileA+".txt")
    smartData = open("data/done/"+fileB+".txt") 
    diffs = []
    for line1, line2 in zip(naiveData, smartData):
        a = float(line1.split()[13])
        b = float(line2.split()[13])
        #print(a,b,a-b)
        diffs.append(a-b)
    print("A is this much slower than B:\t" + str(sum(diffs)/len(diffs)))

def plotLoads():
    s = Simulator()
    seed = 500
    loads = []
    for _ in range(20):
        random.seed(seed)
        s.setupSimulation(numNodes=1000,numTasks=1000000)
        loads = loads + [len(x.tasks) for x in s.nodes.values()]
        seed += 1
    n, bins, patches = plt.hist(loads, 25, normed =1 )
    plt.xlabel('Tasks Per Node')
    plt.ylabel('Probability')
    plt.axvline(statistics.median_low(loads), color='r', linestyle='--')
    plt.show()


def compareTimes():
    data = [7.476, 3.721, 1.558, 5.033, 4.612, 5.673]
    strats = ["None", "Churn", "Random Injection", "Neighbors", "Smart Neighbors", "Invitation"]
    x = np.arange(6)

    plt.bar(x, data, color=['k','w','b','y','g','r'])
    
    plt.xticks(x + 0.5, strats) 
    plt.title('Node Runtimes' )
    plt.legend(loc=0)
    plt.xlabel('Strategy')
    plt.ylabel('Runtime Factor')
    plt.show()

compareTimes()
#drawEvenGraph(10, 100)
#plotLoads()
#compareChurnInjection()
#compareChurnStable()
#compareInjectionStable()
#compareNeighborsStable()
#compareInviteStable()
#compareInviteNeighbor()
#drawAverageChurn("averagesChurnDataPoints")
#drawRandomInjection("averagesRandomInject1k1m")
#printTimeDiffs("averagesNeighbors1k100k", "averagesNeighborsSmart1k100k")
#printTimeDiffs("averagesChurn1k1m", "averagesChurn1h1m")
#printTimeDiffs("averagesChurn1k1m", "averagesChurn1k100k")
#printTimeDiffs("averagesRandomInjection1h10k", "averagesRandomInjection1k100k")
#printTimeDiffs("averagesRandomInjection1h100k", "averagesRandomInjection1k1m")
#printTimeDiffs("averagesRandomInjection1h10k", "averagesRandomInjection1h100k")
#printTimeDiffs("averagesRandomInjection1k100k", "averagesRandomInjection1k1m")
