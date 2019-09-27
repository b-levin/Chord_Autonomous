# integrated variables 
trials = 100
strategies = [ "churn", "randomInjection", "neighbors", "invite"]
homogeneity = ["equal", "randomUniform"] #"randomGauss" ]
workPerTick = ["one", "perStrength"]

"""
workMeasurement:
one:
sybil
strength


homogeneity:
equal: Nodes have the exact same capablities for creating sybils
randomUniform: Nodes have a random uniform  strength
randomGauss: Nodes have a random 

"""




networkSizes = [1000, 5000, 10000]
jobSizes = [100000, 500000, 1000000] #10000000
churnRates = [0, 0.0001, 0.001, 0.01]
adaptationRates = [5]
maxSybils = [5,10]
sybilThresholds = [0, 0.1, 0.25] 
successors = [5,10]

# unintegrated variables








"""
outputs be sure to add average number of tasks done each tick

"""