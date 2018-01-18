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

ALPHA = 0.1
BETHA = 0.1
camino = [(690, 500), (707, 352), (648, 231), (536, 229), (414, 213), (304, 310), (220, 179), (120, 120)]
radang = [(81.98548367283503, 1.0174768393544362), (212.38052384783208, 0.3151827392565967), (257.25247287254206, 0.21679091219737937),
          (171.1774301307442, 0.3531108386774844), (108.58325292727217, 0.8916657834142956), (1484.8192678576224, 0.020894328441807348)]

def calculoAngulo(x1, y1, x2, y2):
    a =  math.atan2(y2-y1, x2-y1)
    while a < 0.0:
        a += math.pi * 2
    return a
class Controller:

    def __init__(self):
        self.pub = rospy.Publisher("/mobile_base/commands/velocity", Twist, queue_size = 20)
        print("ready")

    # Aqui el robot se mueve, ver donde se llama para llenarlo
    def move(self,alpha,betha):
        print "ALFA BETA SON : "
        print(str(alpha) + ", " + str(betha))
        self.pub.publish(Twist(Vector3(alpha, 0.0, 0.0), Vector3(0.0, 0.0, betha)))
        # PUB_MOVE.publish(const.toStringArray(("rotate", ang, "Y")))
        # El primer parametro es la velocidad lineal, y la segunda es la velocidad angular
        for x, y in radang:
            # Ciclos = distancia / velocidad
            # Angulos = angulo / ciclos
            ciclos = int(math.ceil(x/2000))
            angs = y / ciclos
            print "LA DISTANCIA ES : " + str(x)
            print "EL ANGULO ES : " + str(y)
            idx = 0
            for _ in range(ciclos):
                print idx
                idx += 1
                self.pub.publish(Twist(Vector3(ciclos,  0.0, 0.0), Vector3(0.0, 0.0, angs)))
        print "Termine el ciclo"

    def bumper(self):
        self.move(-ALPHA,0)


def move(data):
    data = data.data
    array = np.array(data.split(" "))
    print "???"
    print "ME estan llamando"
    c.move(float(array[0]), float(array[1]))

def bumper(data):
    if data.bumper != 0:
        c.bumper()

def close(data):
    rospy.signal_shutdown("EOF")

if __name__ == "__main__":
    rospy.init_node("KobukiController", anonymous=True)
    rospy.Subscriber("moveController",String,move)
    rospy.Subscriber("/mobile_base/sensors/core",SensorState,bumper)
    rospy.Subscriber("close",String,close)
    c = Controller()
    rospy.spin()

