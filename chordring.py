import matplotlib.pyplot as plt
import numpy as np
import math
import random

def drawGraphBalanced(numNodes):
    xs = []
    ys = []
    fx = []
    fy = []
    randpoints = []
    for _ in range(numNodes):
        num = random.randrange(0.0, 2.0)
        while num in randpoints:
            num = random.uniform(0.0, 2.0)
        randpoints.append(num)
        x = math.cos(num * math.pi)
        y = math.sin(num * math.pi)
        xs.append(x)
        ys.append(y)
    balancedSeed = 0.0
    for _ in range(10):
        x = math.cos(balancedSeed * math.pi)
        y = math.sin(balancedSeed * math.pi)
        fx.append(x)
        fy.append(y)
        balancedSeed += 0.25

    #plt.axes([-1.25,-1.25,1.25,1.25])
    plt.scatter(xs, ys, c="b", marker="+")
    plt.scatter(fx, fy, c="r", marker="o")
    plt.show()

def drawGraphUnbalanced(numNodes):
    xs = []
    ys = []
    fx = []
    fy = []
    randpoints = []
    numList = []
    for _ in range(numNodes):
        num = random.uniform(0.0, 2.0)
        while num in randpoints:
            num = random.uniform(0.0, 2.0)
        randpoints.append(num)
        x = math.cos(num * math.pi)
        y = math.sin(num * math.pi)
        xs.append(x)
        ys.append(y)
    balancedSeed = 0.0
    for _ in range(10):
        num = random.uniform(0.0, 0.25)
        while num in numList:
            num = random.uniform(0.0, 0.25)
        numList.append(num)
        num += balancedSeed
        x = math.cos(num * math.pi)
        y = math.sin(num * math.pi)
        fx.append(x)
        fy.append(y)
        balancedSeed += random.uniform(0.0, 1.0)

    #plt.axes([-1.25,-1.25,1.25,1.25])
    plt.scatter(xs, ys, c="b", marker="+")
    plt.scatter(fx, fy, c="r", marker="o")
    plt.show()

#drawGraphBalanced(100)
drawGraphUnbalanced(100)