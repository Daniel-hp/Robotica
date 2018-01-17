import numpy as np
import random
import math
import rospy
from std_msgs.msg import String

import const
from robot import Robot

class RobotEnvironment:
    
    def __init__(self,x,y,sonar):
        self.sonar = sonar
        self.rob = Robot.getRobot(x,y)
        self.distance = np.zeros((self.rob.num),dtype="float64")
        self.PUB_TKINTER = rospy.Publisher("tkinter", String, queue_size=20)
        if not self.sonar:
            self.triangles = list()
            self.initInterface()
            self.resetInterface()
        
    def __str__(self):
        return str(self.rob)
        
    @staticmethod
    def getRobot(w,h,sonar):
        x = 0.5 * w
        y = 0.5 * h
        return RobotEnvironment(x,y,sonar)
        
    def getDistances(self):
        return self.distance
        
    def getFrontDistance(self):
        return self.distance[0]
        
    def getRearDistance(self):
        if self.rob.num % 2 == 0:
            return self.distance[self.rob.num/2]
        else:
            #X1-Y1
            x1 = self.rob.p[0]
            y1 = self.rob.p[1]
            #X2-Y2
            alpha = self.rob.direction + (const.circle/2.0)
            p = np.array((self.rob.length,0),dtype="float64")
            p = const.rotate(p,alpha)
            p = p + self.rob.p
            x2 = p[0]
            y2 = p[1]
            #X3-Y3
            alpha = self.rob.direction + ((float(int(self.rob.num/2)))*(const.circle/self.rob.num))
            p = np.array((self.rob.length,0),dtype="float64")
            p = const.rotate(p,alpha)
            p = p + self.rob.p
            x3 = p[0]
            y3 = p[1]
            #X4-Y4
            alpha = self.rob.direction + ((float(int(self.rob.num/2) + 1))*(const.circle/self.rob.num))
            p = np.array((self.rob.length,0),dtype="float64")
            p = const.rotate(p,alpha)
            p = p + self.rob.p
            x4 = p[0]
            y4 = p[1]
            d = const.lineIntersection(x1,y1,x2,y2,x3,y3,x4,y4)
            return d
        
    def move(self,total):
        if not self.sonar:
            alpha = self.rob.direction
            p = np.array((total,0),dtype="float64")
            p = const.rotate(p,alpha)
            print "Me encuentro en la posicion: " + str(self.rob.p)
            self.rob.p = p + self.rob.p
            self.canvasDeleteRobot()
            self.canvasRobot()
        
    def rotate(self,total):
        self.rob.direction = (self.rob.direction + total) % const.circle
        if not self.sonar:
            self.canvasDeleteRobot()
            self.canvasRobot()
        
    def initInterface(self):
        w = const.WIDTH
        h = const.HEIGHT
        density = 0.2
        while density > 0:
            if random.random() > 0.5:
                dtype = 0
                area = 1.0/32.0
            else:
                dtype = 1
                area = 2.0/32.0
            polygon = const.getPolygon(dtype)
            polygon = const.expand(polygon,w,h)
            polygon = const.rotatePolygon(polygon,2.0*math.pi*random.random())
            m = np.nanmax(polygon,axis=0)
            m[0] = w - m[0]
            m[1] = h - m[1]
            m[0] = m[0]*random.random()
            m[1] = m[1]*random.random()
            polygon = const.translate(polygon,m[0],m[1])
            polygon = np.around(polygon,decimals=2)
            a = polygon[0,:]
            b = polygon[1,:]
            c = polygon[2,:]
            if not const.inTriangle(self.rob.p,a,b,c):
                if not const.intersectsTriangles(polygon,self.triangles):
                    if not const.insideTriangles(polygon,self.triangles):
                        # Aqui indicar los obstaculos y agregarlos a la lista
                        #self.triangles.append(polygon)
                        density = density - area
        
    def getDistance(self,x2,y2,n):
        w = const.WIDTH
        h = const.HEIGHT
        x1 = self.rob.p[0]
        y1 = self.rob.p[1]
        self.distance[n] = -1.0
        for _ in self.triangles:
            t = _
            for i in xrange(t.shape[0]):
                for j_ in xrange(t.shape[0] - i - 1):
                    j = j_ + i + 1
                    x3 = t[i,0]
                    y3 = t[i,1]
                    x4 = t[j,0]
                    y4 = t[j,1]
                    d = const.lineIntersection(x1,y1,x2,y2,x3,y3,x4,y4)
                    if d > -1.0:
                        if self.distance[n] == -1.0:
                            self.distance[n] = d
                        elif self.distance[n] > d:
                            self.distance[n] = d
        _ = np.array(((0,0),(0,h),(w,h),(w,0)),dtype="float64")  #Es el marco de los limites.
        r = _.shape[0]
        for i in xrange(r):
            x3 = _[i,0]
            y3 = _[i,1]
            x4 = _[(i + 1)%r,0]
            y4 = _[(i + 1)%r,1]
            d = const.lineIntersection(x1,y1,x2,y2,x3,y3,x4,y4)
            if d > -1.0:
                if self.distance[n] == -1.0:
                    self.distance[n] = d
                elif self.distance[n] > d:
                    self.distance[n] = d

    def resume(self):
        for i in xrange(self.rob.num):
            t = "inter" + str(i)
            self.publish(("delete",t))
        n = self.rob.num
        angle = (const.circle) / n
        alpha = self.rob.direction
        for i in xrange(n):
            p = np.copy(self.rob.p)
            if self.distance[i] == -1.0:
                #es paralela o coincidente
                pass
            elif not const.isAlmostCero(self.distance[i]):
                p[0] += self.distance[i]
                p = p - self.rob.p
                tr = np.array(((math.cos(alpha),math.sin(alpha)),(-math.sin(alpha),math.cos(alpha))),dtype="float64")
                p = np.around(np.matmul(p,tr),decimals=2)
                p = p + self.rob.p
                t = "inter" + str(i)
                self.publish(("oval",p[0]-2, p[1]-2, p[0]+2, p[1]+2, "orange",t))
            else:
                pass
            alpha += angle 

        # Dibuja los triangulos
    def canvasTriangles(self):
        obstaculos = [
            [(0, 950), (0, 1000), (1300, 950), (1300, 1000)],  # CHECK
            [(0, 0), (100, 0), (0, 1000), (100, 1000)],  # CHECK
            [(1250, 0), (1300, 0), (1250, 950), (1250, 1000)],  # CHECK
            [(400, 250), (650, 250), (400, 650), (650, 650)],
            [(850, 250), (850, 650), (1100, 250), (1100, 650)]
        ]
        i = 1
        #for _ in self.triangles:
        for _ in range(10):
            arr = _
            t = "Triangle" + str(i)
            i += 1
            '''
            self.publish(("polygon",arr[0,0], arr[0,1], arr[1,0], arr[1,1], arr[2,0], arr[2,1], "red", "black", "gray25",t))
            self.publish("")
            '''
            for z in range(len(obstaculos)):
                for x in range(len(obstaculos[z])):
                    for y in range(len(obstaculos[z])):
                        x0 = obstaculos[z][x][0]
                        y0 = obstaculos[z][x][1]
                        x1 = obstaculos[z][y][0]
                        y1 = obstaculos[z][y][1]
                        #alfa = k.create_line(x0, y0, x1, y1, fill="red")
                        self.publish(("line", x0, y0, x1, y1, "red", t))
                        print "Woot " + str(x0) +" "+ str(y0)+ " "+ str(x1)+ " " + str(y1)
            '''
            x = (arr[0, 0] + arr[1, 0] + arr[2, 0]) / 3.0
            y = (arr[0, 1] + arr[1, 1] + arr[2, 1]) / 3.0
            self.publish(("text", x, y, t))
            '''
            
    def canvasRobot(self):
        x = self.rob.p[0]
        y = self.rob.p[1]
        self.publish(("oval",x-2, y-2, x+2, y+2, "black", "robot"))
        p = np.copy(self.rob.p)
        p[0] += self.rob.length
        angle = (const.circle) / self.rob.num
        alpha = self.rob.direction
        n = 0
        while n < self.rob.num:
            if n == 0:
                col = "red"
            else:
                alpha = angle
                if n == 1:
                    col = "blue"
                else:
                    col = "black"
            t = "line" + str(n)
            p = p - self.rob.p
            p = const.rotate(p,alpha)
            p = p + self.rob.p
            self.publish(("line",x, y, p[0], p[1], col,t))
            self.getDistance(p[0],p[1],n)
            n = n + 1
        self.resume()

    def canvasDeleteRobot(self):
        n = self.rob.num
        self.publish(("delete","robot"))
        while n >= 0:
            t = "line" + str(n)
            self.publish(("delete",t))
            n = n - 1
    
    def publish(self,t):
        s = const.toStringArray(t)
        self.PUB_TKINTER.publish(s)
    
    def resetInterface(self):
        self.publish(("delete","all"))
        self.canvasTriangles()
        self.canvasRobot()

