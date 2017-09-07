#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from Tkinter import *
from random import randint

class Nodo:  # Representa a un punto dentro del mapa
    def __init__(self,coordx, coordy, listaAdyacentes=[]):
        self.coordx = coordx
        self.coordy = coordy
        self.listaAdyacentes = listaAdyacentes

    def agregaAdyacente(self, nodo):
        self.listaAdyacentes.append(nodo)

    def dameCoordenadax(self):
        return self.coordx

    def dameCoordenaday(self):
        return self.coordy

    def __eq__(self, other):
        return self.coordx == other.coordx and self.coordy == other.coordy

    def __repr__(self):
        return "Coordenada x" + str(self.coordx) + " Coordenada y" + str(self.coordy) \
               + " Adyacentes: " + "".join([str(i) for i in self.listaAdyacentes])
    # TODO clase robot
    # class Robot: # Robot que se movera
    # def __init__(self, x, y):
    #	self.coordenadax = x
    #	self.coordenaday = y
    # def mueve(self, ):

ROS_RATE = 10


class Mapa:  # Matriz de celdas
    def __init__(self,longx, longy, obstaculos = [[]], nodos = []):
        self.obstaculos = obstaculos
        self.diccionario = {'longx': longx, 'longy': longy}
        self.nodos= nodos
        self.master = Tk()
    #Dados tres puntos dice si se encuentra en el misom segmento
    @staticmethod
    def enSegmento(x1,y1,x2,y2,x3,y3):
        if min(x1,x3)<= x2 <= max(x1,x3) and min(y1,y3) <= y2 <= max(y1,y3):
            return True
        return False

    #Dados tres puntos regresa la orientacion
    @staticmethod
    def orientacion(x1,y1,x2,y2,x3,y3):
       # print str(x1)+ str(x1)+str(y1)+str(x2)+str(y2)+str(x3)+str(y3)
        val = (y2 - y1) * (x3-x2) - (x2 - x1) * (y3-y2)
        if val == 0:
            return 0
        return 1 if val > 0 else 2

    @staticmethod
    def interseccion(x1,y1,x2,y2,x3,y3,x4, y4):
        o1 = Mapa.orientacion(x1,y1,x2,y2,x3,y3)
        o2 = Mapa.orientacion(x1,y1,x2,y2,x4,y4)
        o3 = Mapa.orientacion(x3,y3,x4,y4,x1,y1)
        o4 = Mapa.orientacion(x3,y3,x4,y4,x2,y2)
        if o1 != o2 and o3 != o4:
            return True
        if o1 == 0 and Mapa.enSegmento(x1, y1, x3, y3, x2, y2):
            return True
        if o2 == 0 and Mapa.enSegmento(x1, y1, x4, y4, x2, y2):
            return True
        if o3 == 0 and Mapa.enSegmento(x3, y3, x1, y1, x4, y4):
            return True
        if o4 == 0 and Mapa.enSegmento(x3, y3, x2, y2, x4, y4):
            return True

        return False

    #doIntersect(Point p1, Point q1, Point p2, Point q2)
    @staticmethod
    def dentroDe(longitud, vertices, x0,y0):
        inf = 100000000000000000000000
        #if longitud <= 3:
        #    return False
        contador = 0
        i =0
        # Se sale del ciclo
        while True:
            sig = (i+1) % longitud
            if  Mapa.interseccion(vertices[i][0], vertices[i][1],vertices[sig][0], vertices[sig][1],
                                 x0,y0,inf,y0):
                if 0 == Mapa.orientacion(vertices[i][0], vertices[i][1],
                                        x0,y0,vertices[sig][0], vertices[sig][1]):
                    return Mapa.enSegmento(vertices[i][0], vertices[i][1],
                                        x0,y0,vertices[sig][0], vertices[sig][1])
                contador +=1
            i = sig
            if i == 0:
                break
        return True if contador%2 == 1 else False
    def dibuja(self):
        k = Canvas(self.master, width=self.diccionario['longx'], height=self.diccionario['longy'])
        k.pack()
        genera = 100
        for x in range(self.diccionario['longx']):
            for y in range(self.diccionario['longy']):
                x1 = x
                y1 = y
                x2 = x1
                y2 = y1
                entro = False
                for z in range(len(self.obstaculos)):
                    if (x,y) in self.obstaculos[z]:
                        k.create_rectangle(x1, y1, x2, y2, fill="blue")
                        entro = True
                if not entro:
                    for z in self.obstaculos:
                        if Mapa.dentroDe(len(z), z,x,y):
                            entro = True
                            break

                if not entro and genera >= 0:
                    lr = 2
                    ## Cambiar por que genera aleatoriamente la coordenada x y la coordenada y
                    if randint(0,500) == 0:
                        k.create_oval(x2, y2, x2, y2, fill="red")
                        genera -= 1
                        self.nodos.append(Nodo(x,y,[]))
                #k.create_oval(x1,y1,x2,y2, fill=color, tags="rect")
                # k.create_rectangle(0+x,0+y,self.diccionario['tamcelda']+x,self.diccionario['tamcelda']+y)
                # k.create_rectangle(y,x,y+10,x+10, fill="red")
                #color = "blue"

        lista_lineas=[]
        for z in range(len(self.obstaculos)):
            for x in range(len(self.obstaculos[z])):
                for y in range(len(self.obstaculos[z])):

                    x0 = self.obstaculos[z][x][0]
                    y0 = self.obstaculos[z][x][1]
                    x1 = self.obstaculos[z][y][0]
                    y1 = self.obstaculos[z][y][1]
                    if x0 != x1 and y0 != y1:
                        seEncuentra = False
                        for al in lista_lineas:
                            # Agregar punto flotante al str
                            arr = [int(k.coords(al)[0]),int(k.coords(al)[1]),int(k.coords(al)[2]),int(k.coords(al)[3])]
                            if arr == [x1,y1,x0,y0]:
                                seEncuentra = True
                        if not seEncuentra:
                            alfa = k.create_line(x0, y0, x1, y1, fill="red" )
                            lista_lineas.append(alfa)

        for x in range(len(self.nodos)):
            for y in range(len(self.nodos)):
                if self.nodos[x] != self.nodos[y]:
                    x0 = self.nodos[x].coordx
                    y0 = self.nodos[x].coordy
                    x1 = self.nodos[y].coordx
                    y1 = self.nodos[y].coordy
                    if abs(x0 - x1) < 100 and abs(y0 - y1) < 100:
                        bool = True
                        for z in lista_lineas:
                            alfa = k.coords(z)

                            #print str(alfa)
                            #print "["+str(x0) + "," + str(y0) + "," + str(x1) + "," + str(y1) + "]|[" + str(alfa[0]) + "," + str(alfa[1]) + "," + str(alfa[2]) + "," + str(alfa[3]) + "]"
                            #print Mapa.interseccion(x0,y0, x1, y1 , alfa[0], alfa[1], alfa[2], alfa[3])
                            if Mapa.interseccion(x0, y0, x1, y1, alfa[0], alfa[1], alfa[2], alfa[3]):
                                bool = False
                        if bool:
                            self.nodos[x].agregaAdyacente(self.nodos[y])
                            alfa = k.create_line(x0, y0, x1, y1)

        def exitros():
            if rospy.is_shutdown():
                self.master.quit()
            self.master.after(ROS_RATE, exitros)
        self.master.after(ROS_RATE, exitros)
        mainloop()


if __name__ == '__main__':
    m1 = Mapa(500,500,[[(0,0),(150,200),(300,110)]])
    # print m1.matriz
    # mainloop()
    m1.dibuja()
    #print Mapa.chocan(1,3,3,3,1,2,3,2)
   ##    print Mapa.interseccion(1,20,50,0,0,0,150,150)
    #print Mapa.interseccion(32,37,94,565,260, 226,2,1)
####
    #####