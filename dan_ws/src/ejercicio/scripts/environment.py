#!/usr/bin/env python

import numpy as np
import random
import math
import rospy
from Tkinter import *
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Vector3
from kobuki_msgs.msg import SensorState

import const
from robotEnvironment import RobotEnvironment

random.seed(42)
GAMMA = const.GAMMA
DISTANCE = const.DISTANCE
ROTATE = const.ROTATE

class Environment:

    def __init__(self,width,height):
        self.PUB_VECTOR = rospy.Publisher("vector", String, queue_size=20)
        self.PUB_MOVE_MAP = rospy.Publisher("moveMap", String, queue_size=20)
        self.PUB_MOVE_CONTROLLER = rospy.Publisher("moveController", String, queue_size=20)
        self.PUB_MOVE = rospy.Publisher("move", String, queue_size=20)
        self.rob = RobotEnvironment.getRobot(width,height,sonar=False)
        self.toMove = 0.0
        self.moveXrotate = True
        self.canMove = False
        self.resetInterface()
        self.buffer = list()
        self.norm = math.pow(self.rob.rob.length,2)
        self.range = const.RANGE
        self.isMin = True
        print("ready")

    def rotate(self,total):
        self.rob.rotate(total)
        self.sendVector()

    def move(self,total):
        self.rob.move(total)
        self.sendVector()

    def resetInterface(self):
        self.rob.resetInterface()

    def sendVector(self):
        s = const.toStringArray(self.rob.getDistances())
        self.PUB_VECTOR.publish(s)

    def requestMove(self,t):
        s = const.toStringArray(t)
        self.PUB_MOVE_MAP.publish(s)

    def getFrontDistance(self):
        return self.rob.getFrontDistance()

    def getRearDistance(self):
        return self.rob.getRearDistance()

    def camposPotenciales(self):
        d = self.rob.getDistances()
        angle = (const.circle) / self.rob.rob.num
        alpha = self.rob.rob.direction
        n = 0
        campo = np.array((0,0),dtype="float64")
        while n < self.rob.rob.num:
            if n != 0:
                alpha = alpha + angle
            if d[n] != -1.0 and d[n] < self.range:
                p = np.array((d[n],0),dtype="float64")
                p = const.rotate(p,alpha)
                l = math.sqrt(math.pow(p[0],2) + math.pow(p[1],2))
                p = p/(l*l*l)
                campo = campo - p
            n = n + 1
        campo = campo * self.norm
        l = math.sqrt(math.pow(campo[0],2) + math.pow(campo[1],2))
        if const.isAlmostCero(l):
            l = 0.0
            alpha = 0.0
        else:
            a = const.rotate(np.array((self.rob.rob.length,0),dtype="float64"),self.rob.rob.direction)
            b = campo
            aux = np.dot(a,b)/(self.rob.rob.length * l)
            if -1.0 >= aux:
                aux = - 0.9
            elif 1.0 <= aux:
                aux = 0.9
            alpha = math.acos(aux)
        return l,alpha

def campos(data):
    rate = rospy.Rate(rospy.get_param('~hz', 10))
    l,r = e.camposPotenciales()
    print("DISTANCE: " + str(l) + " ALPHA: " + str(r))
    if l > e.range:
        l = e.range
    e.buffer.append([-r,"rotate"])
    e.buffer.append([l,"move"])
    e.PUB_MOVE.publish("move")
    if not const.isAlmostCero(l):
        e.isMin = False
    else:
        e.isMin = True

def reset(data):
    e.resetInterface()

def moveMain(data):
    data = data.data
    array = np.array(data.split(" "))
    mode = array[0]
    total = float(array[1])
    override = array[2] == "Y"
    print "La data es : "
    print data
    print(array)
    if not e.canMove or override:
        e.moveXrotate = mode == "move"
        e.toMove = total
        e.canMove = True
        e.buffer = []
        e.isMin = True
        e.PUB_MOVE.publish("move")
    else:
        e.buffer.append([total,mode])

def move(data):
    if e.canMove:
        rate = rospy.Rate(rospy.get_param('~hz', 10))
        if e.moveXrotate:
            if DISTANCE > math.fabs(e.toMove):
                x = e.toMove
                e.canMove = False
            else:
                x = DISTANCE
            if e.toMove > 0:
                d = e.getFrontDistance()
            else:
                d = e.getRearDistance()
            if x > d and d != -1.0:
                x = 0.0
                e.toMove = 0.0
                e.canMove = False
                e.PUB_MOVE.publish("move")
            elif x > (d - x) and d != -1.0:
                x = d - (x * const.SAFE)
            x = math.copysign(x,e.toMove)
            e.toMove = e.toMove - x
            y = 0.0
        else:
            if ROTATE > math.fabs(e.toMove):
                y = e.toMove
                e.canMove = False
            else:
                y = math.copysign(ROTATE,e.toMove)
            x = 0.0
            e.toMove = e.toMove - y
        x = x * GAMMA
        e.PUB_MOVE_CONTROLLER.publish(str(x) + " " + str(y))
        rate.sleep()
        e.PUB_MOVE.publish("move")
    else:
        if e.buffer:
            aux = e.buffer.pop(0)
            e.toMove = aux[0]
            e.moveXrotate = aux[1] == "move"
            e.canMove = True
            e.PUB_MOVE.publish("move")
        elif not e.isMin:
            PUB_VECTOR.publish("vector")

def velocity(data):
    alpha = data.linear.x / GAMMA
    betha = data.angular.z
    if not const.isAlmostCero(alpha):
        e.move(alpha)
        e.requestMove(("move",alpha))
    if not const.isAlmostCero(betha):
        e.rotate(betha)
        e.requestMove(("rotate",betha))

def bumper(data):
    if data.bumper != 0:
        e.canMove = False
        e.toMove = 0.0

def close(data):
    rospy.signal_shutdown("EOF")

if __name__ == "__main__":
    rospy.init_node("EnvironmentSimulation", anonymous=True)
    rospy.Subscriber("requestVector",String,campos)
    rospy.Subscriber("reset",String,reset)
    rospy.Subscriber("moveMain",String,moveMain)
    rospy.Subscriber("move",String,move)
    rospy.Subscriber("/mobile_base/commands/velocity", Twist,velocity)
    rospy.Subscriber("/mobile_base/sensors/core",SensorState,bumper)
    rospy.Subscriber("close",String,close)
    PUB_VECTOR = rospy.Publisher("requestVector", String, queue_size=20)
    w = const.WIDTH
    h = const.HEIGHT
    print(str(w) + ", " + str(h))
    e = Environment(w,h)
    rospy.spin()
