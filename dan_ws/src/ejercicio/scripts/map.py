import numpy as np
import random
import math
from Tkinter import *
import rospy
import const
from robot import Robot

class Map:
    
    def __init__(self,x,y):
        self.width = x
        self.height = y
        self.rob = Robot.getRobot(x/2,y/2)
        self.image = PhotoImage(width=x,height=y)

        #elf.image.put('R0lGODdhEAAQAIcAA neeAAAAAEBAQICAgMDAwQEBAUFBQYGBgcHBwgICAkJCQoKCgsLCwwMDA0NDQ4ODg8PDxAQEBERERISEhMTExQUFBUVFRYWFhcXFxgYGBkZGRoaGhsbGxwcHB0dHR4eHh8fHyAgICEh')
        color = [255 for i in range(0,3)]
        #self.image.put('#%02x%02x%02x' % tuple(color), (0, 0))
        for i in xrange(x):
            for j in xrange(y):
                self.image.put('#%02x%02x%02x' % tuple(color),(0,0))
        
    def move(self,total):
        self.rob.move(total)
    
    def rotate(self,total):
        self.rob.rotate(total)
        
    def setDistances(self,d):
        angle = (const.circle) / self.rob.num
        alpha = self.rob.direction
        n = 0
        color = [0 for i in range(0,3)]
        while n < self.rob.num:
            if n != 0:
                alpha = alpha + angle
            if d[n] != -1.0:
                p = np.array((d[n],0),dtype="float64")
                p = const.rotate(p,alpha)
                p = p + self.rob.p
                p = np.ndarray.astype(p,dtype="int32")
                if p[0] < 0.0:
                    p[0] = 0.0
                elif p[0] >= self.width:
                    p[0] = self.width - 1
                if p[1] < 0.0:
                    p[1] = 0.0
                elif p[1] >= self.height:
                    p[1] = self.height - 1
                self.image.put('#%02x%02x%02x' % tuple(color),(p[0],p[1]))
            n = n + 1
    
