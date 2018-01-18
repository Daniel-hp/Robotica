

import numpy as np
import random
import math
import rospy
import const

class Robot:

    def __init__(self,x,y,length,num,direction):
        # Punto de inicio
        x = 120
        y = 120
        self.p = np.array((x,y),dtype="float64")
        self.length = length
        self.num = num
        self.direction = direction

    def __str__(self):
        return "<" + str(self.p[0]) + ", " + str(self.p[1]) + ", " + str(self.length) + ">"

    @staticmethod
    def getRobot(width,height,length=None):
        if length is None:
            length = const.LENGTH
        num = 6
        direction = 0.75 * const.circle
        return Robot(width,height,length,num,direction)

    def move(self,total):
        alpha = self.direction
        p = np.array((total,0),dtype="float64")
        p = const.rotate(p,alpha)
        self.p = p + self.p

    def rotate(self,total):
        self.direction = (self.direction + total) % const.circle

