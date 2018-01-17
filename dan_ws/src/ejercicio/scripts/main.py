#!/usr/bin/env python
### GRID https://stackoverflow.com/questions/34006302/how-to-create-grid-on-tkinter-in-python
import numpy as np
import random
import math
import time
import rospy
from Tkinter import *
from std_msgs.msg import String

import const
from map import Map

class Prueba:
    def __init__(self, camino, rect = True):
        self.camino = camino
        self.prev = (0,0)
        self.rect = rect
t = "image"
DISTANCE = const.DISTANCE
ROTATE = const.ROTATE
lista_instrucciones = [ "rotate 0.209439510239 Y", "move 1.0 Y" , "rotate -0.209439510239 Y"]
camino = [(690, 500), (707, 352), (648, 231), (536, 229), (414, 213), (304, 310), (220, 179), (120, 120)]
camino.reverse()
rect = True
pr = Prueba(camino)

def suprKey(event):
    PUB_VECTOR.publish("camposPotenciales")
    
def resetKey(event):
    PUB_RESET.publish("reset")
    
def leftKey(event):
    move("rotate",-ROTATE,"Y")
    
def rightKey(event):
    move("rotate",ROTATE,"Y")
    
def upKey(event):
    move("move",DISTANCE,"Y")

def calculoAngulo(x1, y1, x2, y2):
    a =  math.atan2(y2-y1, x2-y1)
    while a < 0.0:
        a += math.pi * 2
    return a


def move(mode,c,override):
    s = const.toStringArray((mode,c,override))
    #print "idx es " + str(idx)
    print("El mensaje es : " + str(s))
    #Se publica el mensaje tanto de movimiento como de rotacion
    cadenas = ("move 1.0 Y", "move 1.0 Y", "move 1.0 Y", "move 1.0 Y")
    rate = rospy.Rate(rospy.get_param('~hz', 10))
    #PUB_MOVE.publish("move 1.0 Y") 
# Pasar una lista con todas las instrucciones e irlas ejecutando cada que el usuario presiona una tecla, paso por paso
    #lista_instrucciones.append(lista_instrucciones[0])
    # Hacer que distancia sea proporcional para evitar cosas rars
    ang = calculoAngulo(camino[0][0], camino[0][1], camino[-1][0], camino[-1][1])
    dist = math.sqrt(math.pow(camino[0][0] - camino[1][0], 2) + math.pow(camino[0][1] - camino[1][1], 2))
    camino.append(camino[0])
    PUB_MOVE.publish(const.toStringArray(("rotate", ang, "Y")))
    rospy.Rate(rospy.get_param('~hz', 10))
    print "...." + str(camino[0])
    print "El angulo es de : " + str(ang)
    camino.pop(0)
    PUB_MOVE.publish(const.toStringArray(("move",  dist, "Y")))
    #if pr.rect:
        #angulo =
    #PUB_MOVE.publish(s)
	 
    
def tkinterListener(data):
    data = data.data
    array = np.array(data.split(" "))
   # print "El array es : " + str(array)
    if array[0] == "delete":
        t = array[1]
        w.delete(t)
        if t == "all":
            resetImage()
    elif array[0] == "line":
        x1 = array[1]
        y1 = array[2]
        x2 = array[3]
        y2 = array[4]
        col = array[5]
        t = array[6]
        w.create_line(x1, y1, x2, y2, fill=col,tag=t)
    elif array[0] == "oval":
        x1 = array[1]
        y1 = array[2]
        x2 = array[3]
        y2 = array[4]
        col = array[5]
        t = array[6]
        w.create_oval(x1, y1, x2, y2, fill=col,tag=t)
    elif array[0] == "polygon":
        x1 = array[1]
        y1 = array[2]
        x2 = array[3]
        y2 = array[4]
        x3 = array[5]
        y3 = array[6]
        col = array[7]
        lin = array[8]
        st = array[9]
        t = array[10]
        w.create_polygon((x1, y1, x2, y2, x3, y3), fill=col,outline=lin,stipple=st,tag=t)
    elif array[0] == "text":
        x = array[1]
        y = array[2]
        t = array[3]
        w.create_text(x,y,text=t)

    
def answerMove(data):
    data = data.data
    array = np.array(data.split(" "))
    total = float(array[1])
    print(array)
    if array[0] == "move":
        m.move(total)
    else:
        m.rotate(total)
    
def setDistances(data):
    data = data.data
    array = np.array(data.split(" "))
    data = const.fromStringArray(const.toStringArray(array))
    m.setDistances(data)
    resetImage()
    
def resetImage():
    w.delete(t)
    w.create_image(x, 0, image = m.image, anchor=NW,tag=t)
    w.update()
    
def on_closing():
    PUB_CLOSE.publish("close")
    master.destroy()
    rospy.signal_shutdown("EOF")
    
if __name__ == "__main__":
    rospy.init_node("main", anonymous=True)
    rospy.Subscriber("tkinter",String,tkinterListener)
    rospy.Subscriber("vector", String, setDistances)
    rospy.Subscriber("moveMap", String, answerMove)
    PUB_VECTOR = rospy.Publisher("requestVector", String, queue_size=20)
    PUB_RESET = rospy.Publisher("reset", String, queue_size=20)
    PUB_MOVE = rospy.Publisher("moveMain", String, queue_size=20)
    PUB_CLOSE = rospy.Publisher("close", String, queue_size=20)
    x = const.WIDTH
    y = const.HEIGHT
    print(str(x) + ", " + str(y))
    master = Tk()
    w = Canvas(master, width=x, height=y)
    m = Map(int(x),int(y))
    w.create_image(x, 0, image = m.image, anchor=NW,tag = t)
    w.bind("<Left>", leftKey)
    w.bind("<Right>", rightKey)
    w.bind("<Up>", upKey)
    w.bind("<Delete>",suprKey)
    w.bind("<BackSpace>",resetKey)
    master.protocol("WM_DELETE_WINDOW", on_closing)
    w.pack()
    w.focus_set()
    mainloop()
