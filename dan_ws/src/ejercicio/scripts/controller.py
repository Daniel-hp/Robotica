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

class Controller:
    
    def __init__(self):
        self.pub = rospy.Publisher("/mobile_base/commands/velocity", Twist, queue_size = 20)
        print("ready")
    
    # Aqui el robot se mueve, ver donde se llama para llenarlo
    def move(self,alpha,betha):
        print(str(alpha) + ", " + str(betha))
	    #alpha = 0.05
	    #betha = 0.0
        # El primer parametro es la velocidad lineal, y la segunda es la velocidad angular
        self.pub.publish(Twist(Vector3(0.0,0.0,alpha),Vector3(0.0,0.0,betha)))

        
    def bumper(self):
        self.move(-ALPHA,0)
        
        
def move(data):
    data = data.data
    array = np.array(data.split(" "))
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
    
