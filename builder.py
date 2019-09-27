from hashlib import sha1
import random
import matplotlib.pyplot as plt
import math

# Global constants
BASE = 160
MAX = 2**BASE

random.seed(12345)


def createStaticIDs(size):
    """
    This creates |size| IDs
    The output will be the same each time we run this. 
    """

    population = sorted([int(sha1(bytes(str(random.random()), "UTF-8")).hexdigest(), 16)
                         % MAX for x in range(size)])
    return population


def generateFileIDs():
    # Create num random file ids
    while True:
        x = random.random()
        yield int(sha1(bytes(str(x), "UTF-8")).hexdigest(), 16) % MAX


if __name__ == '__main__':
    xs = []
    ys = []
    fx = []
    fy = []
    for _ in range(10):
        n = next(generateFileIDs())
        x = math.sin(2 * math.pi * n / MAX)
        y = math.cos(2 * math.pi * n / MAX)
        xs.append(x)
        ys.append(y)

    for _ in range(100):
        n = next(generateFileIDs())
        x = math.sin(2 * math.pi * n / MAX)
        y = math.cos(2 * math.pi * n / MAX)
        fx.append(x)
        fy.append(y)
    #plt.axes([-1.0,1.0,-1.0,1.0] )
    plt.plot(xs, ys, 'ro')
    plt.plot(fx, fy, 'bo')
    plt.show()
