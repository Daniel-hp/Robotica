import numpy as np
import random
import math

circle = 2.0 * math.pi
SIZE = 120.0
WIDTH = 1300 #SIZE * 4.0
HEIGHT = 1000 #SIZE * 3.0
LENGTH = 300.0
GAMMA = 0.01
DISTANCE = 5.0
ROTATE = circle / 30.0
SAFE = 0.5
RANGE = min(WIDTH,HEIGHT) * 0.2

def getPolygon(dtype):
    if dtype == 0:
        return np.array(((0,0),(0,0.25),(0.25,0.25)),dtype="float64")
    else:
        return np.array(((0,0),(0,0.5),(0.25,0.25)),dtype="float64")

def fromStringArray(t):    
    return  np.array(t.split(" "),dtype="float64")
    
def toStringArray(t):
    return ' '.join(str(x) for x in t)
    
def insideTriangles(tr,trs):
    return False
    
def intersectsTriangles(tr,trs):
    for _ in trs:
        t = _
        for i in xrange(t.shape[0]):
            for j_ in xrange(t.shape[0] - i - 1):
                j = j_ + i + 1
                x3 = t[i,0]
                y3 = t[i,1]
                x4 = t[j,0]
                y4 = t[j,1]
                for k in xrange(tr.shape[0]):
                    for l_ in xrange(tr.shape[0] - k - 1):
                        l = l_ + k + 1
                        x1 = tr[k,0]
                        y1 = tr[k,1]
                        x2 = tr[l,0]
                        y2 = tr[l,1]
                        d = lineIntersection(x1,y1,x2,y2,x3,y3,x4,y4)
                        if d != -1.0:
                            return True
    return False
    
def isAlmostCero(num):
    epsilon = 0.05
    return -epsilon < num and num < epsilon
    
def swap(array,i,j):
    aux = np.copy(array[i,:])
    array[i,:] = array[j,:]
    array[j,:] = aux
    return array
    
def multiply(array,i,c):
    array[i,:] = array[i,:] * c
    return array
    
def add(array,i,j,c):
    array[i,:] = array[i,:] + (array[j,:]*c)
    return array
    
def gauss(array):
    for i in xrange(array.shape[0]):
        pos = -1
        for j_ in xrange(array.shape[0] - i):
            j = j_ + i
            if not isAlmostCero(array[j,i]):
                pos = j
        if pos != -1:
            array = swap(array,i,pos)
            array = multiply(array,i,1.0/array[i,i])
            for j_ in xrange(array.shape[0] - i - 1):
                j = j_ + i + 1
                if not isAlmostCero(array[j,i]):
                    array = add(array,j,i,-(array[j,i]))
    return array
    
def jordan(array):
    i = 0
    while(i < array.shape[0]):
        pos = -1
        for j_ in xrange(array.shape[0] - i):
            j = j_ + i
            if not isAlmostCero(array[i,j]):
                pos = j
                break
        if pos == -1:
            break
        else:
            j = pos
        for k in xrange(i):
            _ = array[k,j]
            if not isAlmostCero(_):
                array = add(array,k,i,-(_))
        i += 1
    return array
    
def gaussJordan(array):
    return np.around(jordan(gauss(array)),2)
    
def getPoints(array):
    if array[0,0] == 1.0 and array[1,1] == 1.0:
        return array[0,2],array[1,2]
    elif array[1,2] != 0.0:
        return None,None
    else:
        if array[0,0] == 1.0:
            return array[0,0],None
        elif array[0,1] == 1.0:
            return None,array[0,1]
    return None,None
    
def inRange(x1,x,x2):#
    if x1 > x2:
        aux = x1
        x1 = x2
        x2 = aux
    x1 = x1 - 1
    x2 = x2 + 1
    return x1 <= x and x <= x2
    
def distance(x1,x2,y1,y2):
    return math.sqrt(math.pow(x1 - x2,2) + math.pow(y1 - y2,2))
    
def lineIntersection(x1,y1,x2,y2,x3,y3,x4,y4):
    A1 = y2 - y1
    B1 = x1 - x2
    C1 = (x1*y2) - (x2*y1)
    A2 = y4 - y3
    B2 = x3 - x4
    C2 = (x3*y4) - (x4*y3)
    array = np.array(((A1,B1,C1),(A2,B2,C2)),dtype="float64")
    array = gaussJordan(array)
    px,py = getPoints(array)
    if px is None or py is None:
        if px is None and py is None:
            return -1.0
        else:
            d1 = distance(x1,x3,y1,y3)
            d2 = distance(x1,x4,y1,y4)
            if d1 < d2:
                d = d1
            else:
                d = d2
    else:
        d = distance(x1,px,y1,py)
    if inRange(x1,px,x2) and inRange(y1,py,y2) and inRange(x3,px,x4) and inRange(y3,py,y4):
        return d
    else:
        return -1.0
    
def expand(array,x,y):
    array[:,0] = array[:,0] * x
    array[:,1] = array[:,1] * y
    return array
    
def rotatePolygon(array,alpha):
    array = rotate(array,alpha)
    m = np.nanmin(array,axis=0)
    array = translate(array,-m[0],-m[1])
    return array
    
def rotate(array,alpha):
    tr = np.array(((math.cos(alpha),math.sin(alpha)),(-math.sin(alpha),math.cos(alpha))),dtype="float64")
    array = np.around(np.matmul(array,tr),decimals=2)
    return array
    
def translate(array,x,y):
    array[:,0] = array[:,0] + x
    array[:,1] = array[:,1] + y
    return array
    
def sameSide(p1,p2,a,b):
    cp1 = np.cross(b-a, p1-a)
    cp2 = np.cross(b-a, p2-a)
    if np.dot(cp1, cp2) >= 0:
        return True
    else:
        return False
    
def inTriangle(p,a,b,c):
    if sameSide(p,a,b,c) and sameSide(p,b,a,c) and sameSide(p,c,a,b):
        return True
    else:
        return False

