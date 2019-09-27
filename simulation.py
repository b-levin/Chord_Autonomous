import bisect
import builder
import random
import datetime
import statistics
#maxSybils  = 10
#assert(False)


class Simulator(object):
    def __init__(self):
        pass
       
    def setupSimulation(self, strategy= None, homogeneity= None, workMeasurement=None ,  numNodes = 100, numTasks = 10000, churnRate = 0.01, adaptationRate = 5, maxSybil = 10, sybilThreshold = 0.1, numSuccessors=5):
        self.strategy = strategy
        
        self.nodeIDs = []   # the network topology
        self.superNodes = [] # the nodes that will do the sybilling  
        self.sybils = {} # (node, [] of sybils)
        self.pool = []
        self.nodes = {}  # (id: int, Node: object)
        
        
        self.numNodes = numNodes
        self.numTasks = numTasks
        self.churnRate = churnRate # chance of join/leave per tick per node
        self.adaptationRate = adaptationRate # number of ticks  
        self.maxSybil = maxSybil
        self.sybilThreshold = int((self.numTasks/self.numNodes) * sybilThreshold)
        self.numSuccessors = numSuccessors
        self.homogeneity = homogeneity
        self.workMeasurement = workMeasurement
        
        self.perfectTime = self.numTasks/self.numNodes
        
            
        
        self.numDone = 0
        self.time = 0
        self.numSybils = 0
        
        #self.nodeIDs = builder.createStaticIDs(self.numNodes)
        for _ in range(self.numNodes):
            id = next(builder.generateFileIDs())
            self.nodeIDs.append(id)
            self.superNodes.append(id)
        self.addToPool(self.numNodes)
        
        self.nodeIDs = sorted(self.nodeIDs)
        self.superNodes = sorted(self.superNodes)
        
        #print("Creating Nodes")
        
        expectedWorkPerTick = 0
        for id in self.superNodes:
            n = SimpleNode(id, self.maxSybil, self.homogeneity)
            self.nodes[id] = n
            if workMeasurement == "perStrength":
                expectedWorkPerTick += n.strength
        
        if workMeasurement == "perStrength":
            self.perfectTime = self.numTasks/expectedWorkPerTick
            
        #print("Creating Tasks")
        for key in [next(builder.generateFileIDs()) for _ in range(self.numTasks)]:
            id, _ = self.whoGetsFile(key)
            #print(id % 10000)
            self.nodes[id].addTask(key)
    
        
    def whoGetsFile(self, key : int):
        # returns closest node without going over and it's index in the nodeIDs
        i =  bisect.bisect_left(self.nodeIDs, key) # index of node closest without going over
        if i == len(self.nodeIDs):
            i = 0 
        return self.nodeIDs[i], i
     
    def reallocateTasks(self, tasks):
        for task in tasks:
            index, _  = self.whoGetsFile(task)
            self.nodes[index].addTask(task) 
    
    def doTick(self):
        # assert(len(self.nodeIDs)  ==  len(set(self.nodeIDs)))
        if self.strategy == "randomInjection":
            self.randomInject()
        elif self.strategy == "neighbors":
            #self.neighborInject()
            self.neighborSmart()
        elif self.strategy == "invite":
            self.inviteSybil()
        if not self.churnRate == 0:
            self.churnNetwork() #if churn is 0
        idLoads = [len(self.nodes[x].tasks) for x in self.superNodes]
        loads = [len(x.tasks) for x in self.nodes.values()]
        workThisTick = self.performWork()
        if workThisTick == 0:
            print(idLoads)
            print(loads)
            assert(False)
        self.time += 1
        #print(self.time, self.numDone, workThisTick, len(self.superNodes), len(self.pool), len(self.nodeIDs) )
    
    
    def randomInject(self):
        if (self.time % self.adaptationRate) == 0:
            for nodeID in self.superNodes:
                node = self.nodes[nodeID]
                if (len(node.tasks) <= self.sybilThreshold) and self.canSybil(nodeID):  #what if threshhold is zero?
                    self.addSybil(nodeID)
                
                if nodeID in self.sybils and len(node.tasks) == 0:
                    self.clearSybils(nodeID)
    
    def neighborInject(self):
        if (self.time % self.adaptationRate) == 0:
            for nodeID in self.superNodes:
                node = self.nodes[nodeID]
                if (len(node.tasks) <= self.sybilThreshold) and self.canSybil(nodeID):
                    indexOfSybiler = self.nodeIDs.index(nodeID)
                    firstNeighbor = (indexOfSybiler + 1) % len(self.nodeIDs)
                    lastNeighbor = (indexOfSybiler + 1 + self.numSuccessors) % len(self.nodeIDs)
                    largestGap = 0 
                    boundaryA = -1 
                    boundaryB = -1
                    
                    for i, j in zip(range(indexOfSybiler, lastNeighbor - 1) , range(firstNeighbor, lastNeighbor)):
                        gapSize = (j - i) % builder.MAX
                        if gapSize >largestGap :
                            largestGap = gapSize
                            boundaryA = i
                            boundaryB = j
                    
                    # TODO Unsimplify.  Right now we just cheat and generate a number rather than hashing
                    a = (self.nodeIDs[boundaryA]+1) % builder.MAX 
                    b = (self.nodeIDs[boundaryB] -1) % builder.MAX
                    sybilID = self.mashSimpleNeighbor(a, b)
                    self.addSybil(nodeID, sybilID)
                    #assert((a < sybilID and sybilID < b) or  ()  )
                    
                if nodeID in self.sybils and len(node.tasks) == 0:
                    self.clearSybils(nodeID)
    
    def mashSimpleNeighbor(self, a:int, b :int) -> int:
        if b < a:
            offset = builder.MAX - a 
            b =  b + offset 
            a = 0
            retval  =  (random.randint(a, b) - offset)  % builder.MAX
            return retval
        return random.randint(a, b)   
    
    def neighborSmart(self):
        if (self.time % self.adaptationRate) == 0:
            for nodeID in self.superNodes:
                node = self.nodes[nodeID]
                if (len(node.tasks) <= self.sybilThreshold) and self.canSybil(nodeID):
                    indexOfSybiler = self.nodeIDs.index(nodeID)
                    
                    
                    largestLoad = float("-inf")
                    busiestNodeID = None
                    busiestNodeIndex = None
                    
                    for i in range(indexOfSybiler + 1, indexOfSybiler + 1 + self.numSuccessors):
                        i =  i % len(self.nodeIDs)
                        succID = self.nodeIDs[i]
                        succ = self.nodes[succID]
                        if len(succ.tasks) > largestLoad:
                            busiestNodeID = succID
                            busiestNodeIndex = i
                            largestLoad  =  len(succ.tasks)
                    
                    
                    if largestLoad > len(node.tasks):
                        leftID = self.nodeIDs[busiestNodeIndex -1]
                        sybilID = self.mash(leftID, busiestNodeID)
                        self.addSybil(nodeID, sybilID)
                        
                if nodeID in self.sybils and len(node.tasks) == 0:
                    self.clearSybils(nodeID)
    
                    
                    
    def inviteSybil(self):
        # TODO make sure I'm trying to from the correct gap
        if (self.time % self.adaptationRate) == 0:
            for nodeID in self.superNodes:
                node = self.nodes[nodeID]
                
                if len(node.tasks) >= (self.perfectTime - self.sybilThreshold):   # If I need help
                
                    # grab the index of the node and check with assert
                    index = bisect.bisect_left(self.nodeIDs, nodeID)
                    if index == len(self.nodeIDs):
                        index = 0
                    assert(self.nodeIDs[index] ==nodeID)
                    
                    optimalHelper = None
                    helperLoad = self.sybilThreshold
                    for predIndex in range(index-1 , index-1 -self.numSuccessors, -1):
                        #if predIndex <= len(self.nodeIDs):
                        #    break
                        
                        predID = self.nodeIDs[predIndex]
                        predNode= self.nodes[predID]
                        if (len(predNode.tasks) <= helperLoad) and self.canSybil(predID):
                            optimalHelper = predID
                            helperLoad = len(predNode.tasks)
                    
                    if optimalHelper is not None:
                        #AM I MASHING RIGHT?
                        sybilID = self.mash(self.nodeIDs[index - 1], nodeID)
                        self.addSybil(optimalHelper, sybilID)
                        
                
                if nodeID in self.sybils and len(node.tasks) == 0:
                    self.clearSybils(nodeID)        
    
    def mash(self, a:int, b :int) -> int:
        if abs(b - a) <= 2:
            return a
        a = (a + 1) % builder.MAX
        b = (b - 1) % builder.MAX
        
        if b < a:
            offset = builder.MAX - a 
            b =  b + offset 
            a = 0
            retval  =  (random.randint(a, b) - offset)  % builder.MAX
            return retval
            
        return random.randint(a, b)
    
    def performWork(self):
        """
        equal = default = None: each supernode does one task, regardless of of num of sybils
        strength = each supernode does strength number of tasks
        sybil = node and sybil does one task per tick
        """
        numCompleted = 0
        population = None
        if self.workMeasurement == "one" or self.workMeasurement == 'perStrength':
            population =  self.superNodes
        #elif self.workMeasurement == 'perSybil':
        #    population = self.nodeIDs
        else:
            assert(False)
        for n in population:
            if self.workMeasurement == "perStrength":
                for _ in range(self.nodes[n].strength):
                    workDone = self.nodes[n].doWork()
                    if workDone:  # if the node finished a task
                        self.numDone += 1
                        numCompleted += 1
                    else:
                        break
            elif self.workMeasurement == "one":
                workDone = self.nodes[n].doWork()
                if workDone:  # if the node finished a task
                    self.numDone += 1
                    numCompleted += 1
            else:
                assert(False)
        return numCompleted
        
        #for n in self.sybilIDs:
        #    workDone = self.nodes[n].doWork()
        #    if workDone:  # if the node finished a task
        #        self.numDone += 1
        
        
    def churnNetwork(self):
        """
        figure out who is leaving and store it
        figure out who is joining and store it
        for each leaving node,
            remove it
            collect tasks
        reassign tasks
        
        for each joining
            add new node
            reassign tasks from affected nodes
            
        generate new ids and add them to pool
        
        """
        leaving = []
        joining = []
        for nodeID in self.superNodes:
            if random.random() < self.churnRate:
                leaving.append(nodeID)
        for j in self.pool:
            if random.random() < self.churnRate:
                joining.append(j)
                self.pool.remove(j)
        
        tasks = []
        
        for l in leaving:
            tasks += self.removeNode(l)
        self.reallocateTasks(tasks)
        
        for j in joining:
            # assert(len(self.nodeIDs)  ==  len(set(self.nodeIDs)))
            self.insertWorker(j)
        self.addToPool(len(leaving))
    
    def canSybil(self, superNode):
        if superNode not in self.sybils.keys():
            return True
        return len(self.sybils[superNode]) < self.nodes[superNode].strength
    
    def addSybil(self, superNode, sybilID = None):
        if sybilID is None:
            sybilID =  next(builder.generateFileIDs())
        if superNode not in self.sybils:
            self.sybils[superNode] = [sybilID]
        else:
            self.sybils[superNode].append(sybilID)
        
        self.nodes[sybilID] = self.nodes[superNode]
        self.numSybils += 1
        self.insertWorker(sybilID, self.nodes[sybilID])
        
    def insertWorker(self, joiningID, node = None):
        index  = bisect.bisect(self.nodeIDs, joiningID)
        succID = None
        if index == len(self.nodeIDs): 
            succID = self.nodeIDs[0]
        else:
            succID = self.nodeIDs[index]
        succ =  self.nodes[succID]                
        
        self.nodeIDs.insert(index, joiningID)         
        if node is None:
            node = SimpleNode(joiningID, self.maxSybil, self.homogeneity)
            self.nodes[joiningID] = node
            bisect.insort(self.superNodes, joiningID)
        
        nodeStart = len(node.tasks)
        succStart = len(succ.tasks)
        
        tasks = succ.tasks[:]
        succ.tasks = []
        
        self.reallocateTasks(tasks)
        nodeEnd = len(node.tasks)
        succEnd = len(succ.tasks)
          
    def addToPool(self, num):
        # Adds num nodes to the pool of possible joining nodes
        for _ in range(num):
            x = next(builder.generateFileIDs())
            assert(x not in self.nodeIDs)
            self.pool.append(x)

    def removeNode(self, key):
        # kills a node with the id key
        tasks = self.nodes[key].tasks[:]
        self.superNodes.remove(key)
        self.nodeIDs.remove(key)
        del(self.nodes[key])
        
        # remove all sybils
        if key in self.sybils:
            self.clearSybils(key)
        return tasks
    
    def clearSybils(self, superNode):
        
        for s in self.sybils[superNode]:
            del(self.nodes[s])
            self.numSybils -= 1
            self.nodeIDs.remove(s)
            
            # make sure this gets taken care 
        #assert(False)
        del(self.sybils[superNode])
    
    
    def simulate(self):
        while(self.numDone < self.numTasks):
            self.doTick()
            
        #print(str(self.numTasks) + " done in " + str(self.time) + " ticks.")
        #print(self.perfectTime)
        maxNode =max(self.nodes.values(), key= lambda x: x.done)
        return self.time, maxNode.done
        # print(len(maxNode.done))
    
    def simulateLoad(self):
        loadsList = []
        medians = []
        means = []
        maxs = []
        devs = []
        for _ in range(1,51):
            loads = [len(x.tasks) for x in self.nodes.values()]
            loadsList.append(loads)
            medians.append(statistics.median(loads))
            means.append(statistics.mean(loads))
            maxs.append(max(loads))
            devs.append(statistics.pstdev(loads))
            self.doTick()
        return loadsList, medians, means, maxs, devs

class SimpleNode(object):
    def __init__(self, id, strength, homogeneity):
        self.id = id
        self.strength = strength  #random.randint(1, maxSybils )
        if homogeneity ==  "randomUniform":
            self.strength = random.randint(1, strength)
        elif homogeneity ==  "randomGauss":
            pass
        self.tasks = []
        self.done = 0
    
    def doWork(self):
        if len(self.tasks) > 0:
            self.tasks.pop()
            self.done += 1
            return True
        return False
        
    
    def addTask(self,task):
        self.tasks.append(task)




