#!/usr/bin/env python
from __future__ import division
import rospy
from std_msgs.msg import String
from Tkinter import *
import Tkinter as tk
from random import randint
from collections import deque
import math
import Queue
# TODO clase robot
    # class Robot: # Robot que se movera
    # def __init__(self, x, y):
    #	self.coordenadax = x
    #	self.coordenaday = y
    # def mueve(self, ):

ROS_RATE = 10


class Mapa:  # Matriz de celdas
    def __init__(self,longx, longy, obstaculos = [[]], nodos = [], m = 1):
        self.obstaculos = obstaculos
        self.diccionario = {'longx': longx, 'longy': longy}
        self.nodos= nodos
        self.master = Tk()
        self.m=m
        self.listaLineas =[]
        #Dados tres puntos dice si se encuentra en el mismo segmento
    @staticmethod
    def enSegmento(x1,y1,x2,y2,x3,y3):
        if min(x1,x3)<= x2 <= max(x1,x3) and min(y1,y3) <= y2 <= max(y1,y3):
            return True
        return False

    #Dados tres puntos regresa la orientacion
    @staticmethod
    def orientacion(x1,y1,x2,y2,x3,y3):
        val = (y2 - y1) * (x3-x2) - (x2 - x1) * (y3-y2)
        if val == 0:
            return 0
        return 1 if val > 0 else 2

    # Dados cuatro puntos dice si la linea (x1,y1)-(x2-y2) intersecta
    # con la linea (x3-y3)-(x4-y4)
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

    # Dice si el punto (x0,y0) se encuentra dentro de la lista de obstaculos
    @staticmethod
    def dentroDe(longitud, vertices, x0,y0):
        inf =10000000000000000000000000000
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

    #Dada una ecuacion de linea, una ecuacin de curva y dos intervalos indica si chocan
    @staticmethod
    def chocanIntervalos(linea,curva,lx1,ly1,lx2,ly2,cx1,cy1,cx2,cy2):
        # Se 'igualan ' las ecuaciones a 0
        #To do normal
        if linea[2] is True and curva[3] is True :
            zero = (curva[0],curva[1]-linea[0],curva[2]-linea[1])
            a = zero[0]
            b = zero[1]
            c = zero[2]
            # x = (-b +- sqrt( b^2 - 4ac))/2a
            raiz = math.pow(b,2) - 4 * a * c
            if raiz < 0: # Si la raiz es imaginaria implica no hay interseccion en los numeros reales
                return False
            x1 = (-b + math.sqrt(raiz) )/2*a
            x2 = (-b - math.sqrt(raiz) )/2*a
            # Se sustituye primero x1
            y1 = linea[0]*x1 + linea[1]
            y2 = curva[0] * math.pow(x1,2) + curva[1]*x1 + curva[2]
            # Se obtiene el punto
            intersc1 = (x1,y1)
            y11 = linea[0] * x2 + linea[1]
            y22 = curva[0] * math.pow(x2, 2) + curva[1] * x2 + curva[2]
            intersc2 = (x2,y22)

            cd1 = lx1 <= intersc1 <= lx2 and ly1 <= intersec2 <= ly2 # Se verifica (x,y) esta en la linea
            cd2 = cd1 = lx1 <= intersc1 <= lx2 and ly1 <= intersec2 <= ly2 # Se verifica (x,y) esta en la linea  # Se verifica (x,y) esta en la linea
            cd3 = cx1 <= intersc1 <= cx2 and cy1 <= intersec1 <= cy2 # Se verifica (x,y) esta en la linea
            cd4 = cx1 <= intersc2 <= cx2 and cy1 <= intersec2 <= cy2 # Se verifica (x,y) esta en la linea

            # Primer condicion
            cc1 = cd1 and cd3
            cc2 = cd2 and cd4
            return cc1 or cc2
            # Se verifican los intervalos


    #Para suavizar se crean lineas imaginarias que abarcan el espacio a donde se reduciran, si
    #no chocan se hace la curva, si chocan se vuelve a calcular, ahora a la mitad de la distancia elegida
    # x1y1 pto inicial de primer segmento
    # x2y2 pto final de primer segmento e inicial del segundo
    # x3y3 pto final de segundo segmento
    def segmentoLibre(self, x1,y1,x2,y2,x3,y3):
        # Si x1 == x3 y y1 == y3 se indica que no hay forma de suavizar y se deja
        #la linea recta
        if x1 == x3 and y1 == y3:
            return  (x1, y1, x2, y2, x3, y3)
        # calculamos el punto medio entro x1y1 y x3y3
        ptomediop1p2 = ((x1 + x2) / 2, (y1 + y2) / 2)
        ptomediop2p3 = ((x3 + x2) / 2, (y3 + y2) / 2)
        ptomediop1p3 = ((x3 + x1) / 2, (y3 + y1) / 2)
        # Se calculan los tres puntos arriba de cada punto medio, para trazar las lineas y verificar si chocan con algun obstaculo
        difx1x2 = 0 if x2-x1 == 0 else -1 if x2-x1 < 0 else 1
        dify1y2 = 0 if y2-y1 == 0 else -1 if y2-y1 < 0 else 1
        difx3x2 = 0 if x2-x3 == 0 else -1 if x2-x3 < 0 else 1
        dify3y2 = 0 if y2-y3 == 0 else -1 if y2-y3 < 0 else 1
        ptosx1y1x2y2 = [ptomediop1p2] + [(ptomediop1p2[0] + difx1x2, ptomediop1p2[1] + dify1y2),
                                         (ptomediop1p2[0] + difx1x2 * 2, ptomediop1p2[1] + dify1y2 * 2),
                                        (ptomediop1p2[0] + difx1x2 * 3, ptomediop1p2[1] + dify1y2 * 3)]
        ptosx3y3x2y2= [ptomediop2p3] + [(ptomediop2p3[0] + difx3x2, ptomediop2p3[1] + dify3y2),
                                        (ptomediop2p3[0] + difx3x2 * 2, ptomediop2p3[1] + dify3y2 * 2),
                                        (ptomediop2p3[0] + difx3x2 * 3, ptomediop2p3[1] + dify3y2 * 3)]
        # Hacer que si los pts medios coinciden se regresa esa coordenada
        for alfa in self.listaLineas:
            for x in ptosx1y1x2y2:
                for y in ptosx3y3x2y2:
                    if Mapa.interseccion(x[0],x[1],y[0],y[1],
                                        alfa[0], alfa[1], alfa[2], alfa[3]):
                        return self.segmentoLibre(ptomediop1p2[0],ptomediop1p2[1],x2,y2,ptomediop2p3[0],ptomediop2p3[1])
        return (ptomediop1p2[0], ptomediop1p2[1], ptomediop1p3[0], ptomediop1p3[1], ptomediop2p3[0], ptomediop2p3[1])

    # Dado un conjunto de puntos suaviza las lineas rectas entre estos
    def suaviza(self, ptos, k):
        # Se agarra el punto x[i], x[i+1], x[i+2]
        # Y se observa si se puede suavizar la linea x[i]x[i+1]  x[i+1]x[i+2]
        long = len(ptos)
        x = 0
        #Se suaviza la linea
        nvosptos = []
        print long
        while x+2 < long :
            pto1x = ptos[x].estado.dameCoordenadax()
            pto1y = ptos[x].estado.dameCoordenaday()
            pto2x = ptos[x + 1].estado.dameCoordenadax()
            pto2y = ptos[x + 1].estado.dameCoordenaday()
            pto3x = ptos[x + 2].estado.dameCoordenadax()
            pto3y = ptos[x + 2].estado.dameCoordenaday()

            segmentos = self.segmentoLibre(pto1x,pto1y,pto2x,pto2y,pto3x,pto3y)
            print segmentos
            angulos =  Mapa.calculaCirculo(segmentos[0],segmentos[1],
                                           segmentos[2],segmentos[3],
                                           segmentos[4],segmentos[5])

            print angulos
            k.create_arc(angulos[0],angulos[1],angulos[2],angulos[3],
                         start=angulos[4], extent=angulos[4] -angulos[5],style=tk.ARC)
           # k.create_line(pto1x,pto1y,
           #               segmentos[0], segmentos[1])
           # k.create_line(segmentos[0], segmentos[1],
           #               segmentos[2], segmentos[3])
           # k.create_line(segmentos[2], segmentos[3],
           #               segmentos[4], segmentos[5])
           # k.create_line(segmentos[4], segmentos[5],
           #               pto3x,pto3y)
           # print segmentos
           # print "["+ str(pto1x) + "," \
           #         +str(pto1y)+ ","  + str(pto2x) + ","  + \
           #       str(pto2y) + ","  +  str(pto3x) + ","  + str(pto3y) + "]"

            x += 2
        # Los sobrantes se dejan con la linea recta
        if x + 2 == long:
            pto1x = ptos[x].estado.dameCoordenadax()
            pto1y = ptos[x].estado.dameCoordenaday()
            pto2x = ptos[x + 1].estado.dameCoordenadax()
            pto2y = ptos[x + 1].estado.dameCoordenaday()
            k.create_line(pto1x,pto1y,pto2x,pto2y)
        return (nvosptos, long - x)

    @staticmethod
    def calculaCirculo(x1,y1,x2,y2,x3,y3):
       if x1 == x2 or x2 == x1 :
            return False
       ptomd1 = ((x1+x2)/2, (y1+y2)/2)
       ptomd2 = ((x2+x3)/2, (y2+y3)/2)
        #print ptomd1
        #print ptomd2
       pend1 = (y2-y1)/(x2-x1)
       pend2 = (y3-y2)/(x3-x2)
        #print pend1
        #print pend2
        # y = mx + b  => (y,mx,b)
       ec1 = (1, pend1, -pend1 * ptomd1[0] + ptomd1[1])
       ec2 = (1, pend2, -pend2 * ptomd2[0] + ptomd2[1])
        #print ec1
        #print ec2
        # Se igualan las y, se resuelve por x
       x = (ec2[2] - ec1[2]) / -(ec2[1] - ec1[1])
       y = x * ec1[1] + ec1[2]
       # (x,y) representa el centro del circulo
       r = math.sqrt(math.pow(x-ptomd1[0],2) + math.pow(y-ptomd1[1],2))
       primpto = (x-r,y+r)
       segpto = (x-r,y-r)
       tercerpto = (x+r,y+r)
       crtopto = (x+r,y-r)

       alfa = math.degrees(math.atan2((ptomd2[1] - y) ,(ptomd2[0] - x)))
       beta = math.degrees(math.atan2((ptomd1[1] - y) , (ptomd1[0] - x)))
       return (x-r,y+r,x+r,y-r,alfa,beta)

    def calcula(self):
        self.nodos.append(Nodo(0, 250, []))
        self.nodos.append(Nodo(499, 499, []))
        k = Canvas(self.master, width=self.diccionario['longx'], height=self.diccionario['longy'])
        k.pack()
        k.create_oval(0, 499, 0, 499, fill="red")
        k.create_oval(499, 499, 499, 499, fill="red")
        genera = 60
        while genera > 0:
            entro = False
            x = randint(0, self.diccionario['longx'])
            y = randint(0, self.diccionario['longx'])

            # Verifica no exista el nodo ya en la lista
            for z in range(len(self.nodos)):
                a = Nodo(x, y, [])

                if a == self.nodos[z]:
                    entro = True
            # Si no esta en la lista verifica no sea un obstaculo
            if not entro:
                for z in range(len(self.obstaculos)):
                    if (x, y) in self.obstaculos[z]:
                        entro = True
            # Si no esta en la lista ni es obstaculo verifica no esta dentro de un obstaculo
            if not entro:
                for z in self.obstaculos:
                    if Mapa.dentroDe(len(z), z, x, y):
                        entro = True
                        break
            # Si no entro se genera el nodo  y se disminuye en 1 el genera
            if not entro:
                if randint(0, 500) == 0:
                    k.create_oval(x, y, x, y, fill="red")
                    genera -= 1
                    self.nodos.append(Nodo(x, y, []))
        self.listaLineas = []
        # Para dibujar la linea entre los obstasculos
        for z in range(len(self.obstaculos)):
            for x in range(len(self.obstaculos[z])):
                for y in range(len(self.obstaculos[z])):
                    x0 = self.obstaculos[z][x][0]
                    y0 = self.obstaculos[z][x][1]
                    x1 = self.obstaculos[z][y][0]
                    y1 = self.obstaculos[z][y][1]
                    if x0 != x1 and y0 != y1:
                        seEncuentra = False
                        for al in self.listaLineas:
                            arr = [al[0], al[1],al[2],al[3]]
                            if arr == [x1, y1, x0, y0]:
                                seEncuentra = True
                        if not seEncuentra:
                            alfa = k.create_line(x0, y0, x1, y1, fill="red")
                            self.listaLineas.append(k.coords(alfa))
        # Para dibujar la linea entre los puntos verificando estas no choquen y
        for x in range(len(self.nodos)):
            for y in range(len(self.nodos)):
                if self.nodos[x] != self.nodos[y]:
                    x0 = self.nodos[x].coordx
                    y0 = self.nodos[x].coordy
                    x1 = self.nodos[y].coordx
                    y1 = self.nodos[y].coordy
                    if abs(x0 - x1) <200 and abs(y0 - y1) < 200:
                        bool = True
                        for z in self.listaLineas:

                            if Mapa.interseccion(x0, y0, x1, y1, z[0], z[1], z[2], z[3]):
                                bool = False
                        if bool:
                            self.nodos[x].agregaAdyacente(self.nodos[y])
                            k.create_line(x0, y0, x1, y1)

        def exitros():
            if rospy.is_shutdown():
                self.master.quit()
            self.master.after(ROS_RATE, exitros)
        self.master.after(ROS_RATE, exitros)

        mainloop()

class Nodo:  # Representa a un punto dentro del mapa
    def __init__(self, coordx, coordy, listaAdyacentes=[]):
        self.coordx = coordx
        self.coordy = coordy
        self.listaAdyacentes = listaAdyacentes
        self.hn = 0
        self.gn = 0
        self.visitado = False
        self.sol = False
        self.listaCerrada = False
        self.listaAbierta = False

    def dameVisitado(self):
        return self.visitado

    def damefn(self):
        return self.gn + self.hn()

    def damehn(self):
        return self.hn

    def agregaAdyacente(self, nodo):
        self.listaAdyacentes.append(nodo)

    def dameAdyacentes(self):
        return self.listaAdyacentes

    def dameCoordenadax(self):

        return self.coordx

    def dameCoordenaday(self):
        return self.coordy

    def __key(self):
        return (self.coordx,self.coordy)

    def __eq__(self, other):
        return self.__key() == other.__key()


    def __str__(self):
        return  "("+str(self.coordx) + " , " + str(self.coordy)+")"
    def __repr__(self):
        return "("+str(self.coordx) + " , " + str(self.coordy) + ")"
    def __hash__(self):
        return hash(self.__key())

class AEstrella:
    # Devolver False en caso de que no se haya encontrado solucion
    def __init__(self,inicio,meta, nodos = []):
        self.inicio = inicio
        self.iinicioNB = NodoBusqueda(None,inicio)
        self.meta = meta
        self.metaNB = NodoBusqueda(None,meta)
        self.nodos = nodos
        self.listaAbierta = Queue.PriorityQueue()
        self.listaCerrada = {}
        self.solucion = []
        self.resuleto = False
        inicio.hn = AEstrella.calculaHeuristica(inicio,meta)
        self.nodoActual = None
        self.nodoPrevio = NodoBusqueda(None,inicio)
        self.listaAbierta.put(self.nodoPrevio)

    @staticmethod
    def calculaHeuristica(n1,n2):

        return math.hypot(n2.dameCoordenadax() - n1.dameCoordenadax(),
                          n2.dameCoordenaday() - n1.dameCoordenaday())

    def expandeNodoSiguiente(self):
        if self.resuleto:
            return
        self.nodoActual = self.listaAbierta.get()
        self.listaCerrada[self.nodoPrevio.estado] = self.nodoPrevio.estado
        self.nodoPrevio.estado.listaCerrada=True
        if self.nodoActual.estado == self.meta:
            self.resuleto = True
            tmp = self.nodoActual
            while tmp.estado != self.inicio:
                self.solucion.append(tmp)
                tmp.estado.sol = True
                tmp = tmp.padre
            self.solucion.append(tmp)
        else:
            suc = self.nodoActual.getSucesores()
            for sucesor in suc:
                if not sucesor.estado.listaCerrada:
                    if not sucesor.estado.listaAbierta:
                        sucesor.estado.hn = sucesor.calculaDistancia(self.meta) + NodoBusqueda.calculaAngulo(sucesor,self.metaNB)
                        sucesor.estado.gn = sucesor.gn + sucesor.calculaDistancia(sucesor.padre.estado) # Se agrega el costo dellegar al nodo
                        self.listaAbierta.put(sucesor)
                        sucesor.estado.listaCerrada = True
                else:
                    sucesor.estado.gn = sucesor.gn
                    sucesor.estado.padre = sucesor.padre.estado
        self.nodoPrevio = self.nodoActual


class NodoBusqueda:
    def __init__(self, padre,estado, m=1):
        self.padre = padre
        self.estado = estado
        self.gn = 0
        self.m = m
# Verificar cuando calcular lo del angulo
    def setGn(self, gn):
        self.gn = gn
    def calculahn(self):
        return 0
    def dameFn(self):
        return self.estado.damehn() + self.gn

    def calculaDistancia(self, n1):
        return math.hypot(self.estado.dameCoordenadax() - n1.dameCoordenadax(),
                          self.estado.dameCoordenaday() - n1.dameCoordenaday())

    # Dado un punto n, calcula el angulo que se forma al intentar llegar a este, dado que hay
    @staticmethod
    def calculaAngulo(n1,n2):
        # Ver que acos siempre se ejecute
        # Si el nodo es el inicio  no hay angulo que calcular
        if n1.padre is None:
            return 1
        a = n1.padre.estado
        b = n1.estado
        c = n2.estado
        if a == c: # El nodo intenta calcular el angulo de  a --- b --- a
            return 360
        ab = math.sqrt(math.pow(a.dameCoordenadax()-b.dameCoordenadax(),2)
              + math.pow(a.dameCoordenaday() - b.dameCoordenaday(),2))
        bc = math.sqrt(math.pow(c.dameCoordenadax()-b.dameCoordenadax(),2)
              + math.pow(c.dameCoordenaday() - b.dameCoordenaday(),2))
        ca = math.sqrt(math.pow(a.dameCoordenadax()-c.dameCoordenadax(),2)
              + math.pow(a.dameCoordenaday() - c.dameCoordenaday(),2))

        numerador = math.pow(ab,2) + math.pow(ca,2) - math.pow(bc,2)
        denominador = 2 * ab * ca
        if denominador == 0:
            return 0
        resultado =math.acos(numerador / denominador)
        return math.degrees(resultado)
    def getSucesores(self):
        sucesores = deque()
        for x in self.estado.dameAdyacentes():
            nodoSucesor = NodoBusqueda(self,x)
            dem = pow(NodoBusqueda.calculaAngulo(self,nodoSucesor),2)
            if dem != 0:
                nodoSucesor.gn = self.gn + self.calculaDistancia(x) * (1 / dem) * self.m
            nodoSucesor.gn = 100000
            sucesores.append(nodoSucesor)
        return sucesores

    def __cmp__(self,nb1):
        return self.dameFn() - nb1.dameFn()

    def __repr__(self):
        return str(self.estado)


if __name__ == '__main__':
    m1 = Mapa(500,500,[[(0,0),(150,200),(300,110)],[(50,50),(25,25),(25,50),(50,25)]])
    m1.calcula()
    alg = AEstrella(m1.nodos[0], m1.nodos[1], m1.nodos)
    num = 500
    while not alg.resuleto and num > 0:
        alg.expandeNodoSiguiente()
        num -=1
        print num
    master = Tk()
    k = Canvas(master, width=500, height=500)
    k.pack()
    #Se dibujan las lineas del recorrido obtenido por A*
    for x in range(len(alg.solucion)):
        k.create_rectangle(alg.solucion[x].estado.dameCoordenadax(),
                           alg.solucion[x].estado.dameCoordenaday(),
                           alg.solucion[x].estado.dameCoordenadax(),
                           alg.solucion[x].estado.dameCoordenaday()
        )
    # Para evitar hacer una linea de la meta al inicio
        if x != len(alg.solucion)-1:
            k.create_line(alg.solucion[x].estado.dameCoordenadax(),
                      alg.solucion[x].estado.dameCoordenaday(),
                      alg.solucion[(x+1)% len(alg.solucion)].estado.dameCoordenadax(),
                      alg.solucion[(x+1)%len(alg.solucion)].estado.dameCoordenaday())

    # Se suavizan las lineas obtenidasd anteriormente
    #print alg.solucion[0]
    #k.create_arc(alg.solucion[0].estado.dameCoordenadax(),
     #            alg.solucion[0].estado.dameCoordenaday(),
      #           alg.solucion[-1].estado.dameCoordenadax(),
       #           alg.solucion[-1].estado.dameCoordenaday(),
        #         style=tk.ARC)

   # k.create_arc(0, 0, 500, 500)
    #master.after(ROS_RATE, exitros)
    mainloop()
    #print m1.segmentoLibre(0,0,50,50,100,100)
    master = Tk()
    k = Canvas(master, width=500, height=500)
    k.pack()

    m1.suaviza(alg.solucion, k)
    mainloop()
    #master = Tk()
    #k = Canvas(master, width=500, height=500)
    #k.pack()
    #k.create_rectangle(0,15,0,15)
    #k.create_rectangle(100,25,100,25)
    #k.create_rectangle(50,50,50,50)
    #mainloop()
    #master = Tk()
    #k = Canvas(master, width=500, height=500)
    #k.pack()
    #angulos =  Mapa.calculaCirculo(0,15,100,25,50,50)
    #print angulos
    #k.create_arc(0,15,50,50,start = angulos[0], extent = angulos[1], style=tk.ARC)
    #mainloop()
    #print Mapa.ecuacionCuadratica(2,5,7    ,7,9,9)
