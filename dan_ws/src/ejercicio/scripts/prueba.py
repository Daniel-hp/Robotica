#!/usr/bin/env python
from __future__ import division
import rospy
from Tkinter import *
import Tkinter as tk
from random import randint
from collections import deque
import math
from std_msgs.msg import String
import Queue

ROS_RATE = 10


###
##ARCO
# https://math.stackexchange.com/questions/390272/drawing-an-arc-between-two-points
###
# INTERSECCICON ENTRE ARCO Y LINEA
# https://stackoverflow.com/questions/30006155/calculate-intersect-point-between-arc-and-line

radang = []
class Mapa:  # Matriz de celdas
    def __init__(self, longx, longy, obstaculos=[[]], nodos=[], m=1):
        self.obstaculos = obstaculos
        self.diccionario = {'longx': longx, 'longy': longy}
        self.nodos = nodos
        self.master = Tk()
        self.m = m
        self.listaLineas = []
        self.caminoS = []
        # Dados tres puntos dice si se encuentra en el mismo segmento

    @staticmethod
    def enSegmento(x1, y1, x2, y2, x3, y3):
        if min(x1, x3) <= x2 <= max(x1, x3) and min(y1, y3) <= y2 <= max(y1, y3):
            return True
        return False

    # Dados tres puntos regresa la orientacion
    @staticmethod
    def orientacion(x1, y1, x2, y2, x3, y3):
        val = (y2 - y1) * (x3 - x2) - (x2 - x1) * (y3 - y2)
        if val == 0:
            return 0
        return 1 if val > 0 else 2

    # Dados cuatro puntos dice si la linea (x1,y1)-(x2-y2) intersecta
    # con la linea (x3-y3)-(x4-y4)
    @staticmethod
    def interseccion(x1, y1, x2, y2, x3, y3, x4, y4):
        o1 = Mapa.orientacion(x1, y1, x2, y2, x3, y3)
        o2 = Mapa.orientacion(x1, y1, x2, y2, x4, y4)
        o3 = Mapa.orientacion(x3, y3, x4, y4, x1, y1)
        o4 = Mapa.orientacion(x3, y3, x4, y4, x2, y2)
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
    def dentroDe(longitud, vertices, x0, y0):
        inf = 10000000000000000000000000000
        contador = 0
        i = 0
        # Se sale del ciclo
        while True:
            sig = (i + 1) % longitud
            if Mapa.interseccion(vertices[i][0], vertices[i][1], vertices[sig][0], vertices[sig][1],
                                 x0, y0, inf, y0):
                if 0 == Mapa.orientacion(vertices[i][0], vertices[i][1],
                                         x0, y0, vertices[sig][0], vertices[sig][1]):
                    return Mapa.enSegmento(vertices[i][0], vertices[i][1],
                                           x0, y0, vertices[sig][0], vertices[sig][1])
                contador += 1
            i = sig
            if i == 0:
                break
        return True if contador % 2 == 1 else False

    #Metodo que calcula :
    #
    #        ( ||AC||^2 - ||BC||^2 - ||AB||^2 )
    #C = acos(---------------------------------)
    #        (-2 ||BC|| * ||AB||               )
    #
    @staticmethod
    def aRobot(x1,y1,rx,ry,x2,y2):
        # Primero se restan las coordenadas para obtener el vector
        lonAC = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
        lonBC = math.sqrt(math.pow(x2 - rx, 2) + math.pow(y2 - ry, 2))
        lonAB = math.sqrt(math.pow(x1 - rx, 2) + math.pow(y1 - ry, 2))
        numerador = math.pow(lonAC,2) - math.pow(lonBC,2) - math.pow(lonAB,2)
        denominador = -2 * lonBC * lonAB

        '''
        vectAR = (x1 - rx, y1 - rx)
        vectRB = (rx - x2, ry - y2)
        prodPto = vectAR[0] * vectRB[0] + vectAR[1] * vectRB[1]
        dist1 = math.sqrt(math.pow(x1 - rx, 2) + math.pow(y1 - ry, 2))
        dist2 = math.sqrt(math.pow(rx - x2, 2) + math.pow(ry - y2, 2))
        print prodPto
        print dist1
        print dist2
        '''
        return math.acos(numerador / denominador)
        #return math.acos(prodPto / ((dist1) * (dist2)))
    # Para suavizar se crean lineas imaginarias que abarcan el espacio a donde se reduciran, si
    # no chocan se hace la curva, si chocan se vuelve a calcular, ahora a la mitad de la distancia elegida
    # x1y1 pto inicial de primer segmento
    # x2y2 pto final de primer segmento e inicial del segundo
    # x3y3 pto final de segundo segmento
    def segmentoLibre(self, x1, y1, x2, y2, x3, y3):
        # Si x1 == x3 y y1 == y3 se indica que no hay forma de suavizar y se deja
        # la linea recta
        if x1 == x3 and y1 == y3:
            return (x1, y1, x2, y2, x3, y3)
        # calculamos el punto medio entro x1y1 y x3y3
        ptomediop1p2 = ((x1 + x2) / 2, (y1 + y2) / 2)
        ptomediop2p3 = ((x3 + x2) / 2, (y3 + y2) / 2)
        ptomediop1p3 = ((x3 + x1) / 2, (y3 + y1) / 2)
        # Se calculan los tres puntos arriba de cada punto medio, para trazar las lineas y verificar si chocan con algun obstaculo
        difx1x2 = 0 if x2 - x1 == 0 else -1 if x2 - x1 < 0 else 1
        dify1y2 = 0 if y2 - y1 == 0 else -1 if y2 - y1 < 0 else 1
        difx3x2 = 0 if x2 - x3 == 0 else -1 if x2 - x3 < 0 else 1
        dify3y2 = 0 if y2 - y3 == 0 else -1 if y2 - y3 < 0 else 1
        ptosx1y1x2y2 = [ptomediop1p2] + [(ptomediop1p2[0] + difx1x2, ptomediop1p2[1] + dify1y2),
                                         (ptomediop1p2[0] + difx1x2 * 2, ptomediop1p2[1] + dify1y2 * 2),
                                         (ptomediop1p2[0] + difx1x2 * 3, ptomediop1p2[1] + dify1y2 * 3)]
        ptosx3y3x2y2 = [ptomediop2p3] + [(ptomediop2p3[0] + difx3x2, ptomediop2p3[1] + dify3y2),
                                         (ptomediop2p3[0] + difx3x2 * 2, ptomediop2p3[1] + dify3y2 * 2),
                                         (ptomediop2p3[0] + difx3x2 * 3, ptomediop2p3[1] + dify3y2 * 3)]
        # Hacer que si los pts medios coinciden se regresa esa coordenada
        for alfa in self.listaLineas:
            for x in ptosx1y1x2y2:
                for y in ptosx3y3x2y2:
                    if Mapa.interseccion(x[0], x[1], y[0], y[1],
                                         alfa[0], alfa[1], alfa[2], alfa[3]):
                        return self.segmentoLibre(ptomediop1p2[0], ptomediop1p2[1], x2, y2, ptomediop2p3[0],
                                                  ptomediop2p3[1])
        return (ptomediop1p2[0], ptomediop1p2[1], ptomediop1p3[0], ptomediop1p3[1], ptomediop2p3[0], ptomediop2p3[1])

    # Dado un conjunto de puntos suaviza las lineas rectas entre estos
    def suaviza(self, ptos, k):
        # Se agarra el punto x[i], x[i+1], x[i+2]
        # Y se observa si se puede suavizar la linea x[i]x[i+1]  x[i+1]x[i+2]
        long = len(ptos)
        x = 0
        # Se suaviza la linea
        nvosptos = []
        print long
        print "Los puntos son :  [" + str(ptos) + "]"
        if long <= 2:
            pto1x = ptos[x].estado.dameCoordenadax()
            pto1y = ptos[x].estado.dameCoordenaday()
            pto2x = ptos[x + 1].estado.dameCoordenadax()
            pto2y = ptos[x + 1].estado.dameCoordenaday()
            k.create_line(pto1x, pto1y, pto2x, pto2y)
        else:
            # Se dibuja la primer linea
            pto1x = ptos[x].estado.dameCoordenadax()
            pto1y = ptos[x].estado.dameCoordenaday()
            pto2x = ptos[x + 1].estado.dameCoordenadax()
            pto2y = ptos[x + 1].estado.dameCoordenaday()
            k.create_line(pto1x, pto1y, (pto1x + pto2x) / 2, (pto1y + pto2y) / 2)
            while x + 2 < long:
                pto1x = ptos[x].estado.dameCoordenadax()
                pto1y = ptos[x].estado.dameCoordenaday()
                pto2x = ptos[x + 1].estado.dameCoordenadax()
                pto2y = ptos[x + 1].estado.dameCoordenaday()
                pto3x = ptos[x + 2].estado.dameCoordenadax()
                pto3y = ptos[x + 2].estado.dameCoordenaday()
                angulos = Mapa.calculaCirculo(pto1x, pto1y,
                                              pto2x, pto2y,
                                              pto3x, pto3y, k)
                self.caminoS = self.caminoS + [(angulos[0], angulos[1], angulos[2], angulos[3], angulos[4], angulos[5])]
                k.create_arc(angulos[0], angulos[1], angulos[2], angulos[3],
                             start=-angulos[5], extent=angulos[5] - angulos[4], style=tk.ARC, fill="green")
                # start=-angulos[5], extent=angulos[5] - angulos[4]
                x += 1
            # Los sobrantes se dejan con la linea recta
            pto1x = ptos[x].estado.dameCoordenadax()
            pto1y = ptos[x].estado.dameCoordenaday()
            pto2x = ptos[x + 1].estado.dameCoordenadax()
            pto2y = ptos[x + 1].estado.dameCoordenaday()
            k.create_line((pto1x + pto2x) / 2, (pto2y + pto1y) / 2, pto2x, pto2y)

    # El centro del circulo esta dado por (x0,y0)
    @staticmethod
    def calcula_arco(x0, y0, x1, y1, x2, y2):
        # El radio del punto (x1,y1) a (x0,y0)
        radio = math.sqrt((x1-x0)**2 + (y1-y0)**2)
        x = x0-radio
        y = y0-radio
        angulo_inicial = 180 / (math.pi * math.atan2(y1-y0,x1-x0))
        angulo_final = 180 / (math.pi * math.atan2(y2-y0,x2-x0))
        return x, y, angulo_inicial, angulo_final
    @staticmethod
    def calculaCirculo(x1, y1, x2, y2, x3, y3, k):
        ptomd1 = ((x1 + x2) / 2, (y1 + y2) / 2)
        ptomd2 = ((x2 + x3) / 2, (y2 + y3) / 2)
        #k.create_rectangle(x1, y1, x1 + 10, y1 + 10, fill="green")
        #k.create_rectangle(x2, y2, x2 + 10, y2 + 10, fill="green")
        #k.create_rectangle(x3, y3, x3 + 10, y3 + 10, fill="green")
        #k.create_rectangle(ptomd1[0], ptomd1[1], ptomd1[0] + 10, ptomd1[1] + 10)
        #k.create_rectangle(ptomd2[0], ptomd2[1], ptomd2[0] + 10, ptomd2[1] + 10)
        # Las lineas comentadas corresponden a los circulos formados
        # previamente
        '''
        if x1 == x2 or x2 == x1:
            return False
        k.create_rectangle(ptomd1[0], ptomd1[1], ptomd1[0]+10, ptomd1[1]+10, fill="cyan")
        k.create_rectangle(ptomd2[0], ptomd2[1], ptomd2[0]+10, ptomd2[1]+10, fill="cyan")
        if y2 - y1 == 0:
            pend1 = 0
        else:
            pend1 = -(x2 - x1) / (y2 - y1)
        if y2 - y3 == 0:
            pend2 = 0
        else:
            pend2 = -(x2 - x3) / (y2 - y3)
            # print pend1
            # print pend2
            # y = mx + b  => (y,mx,b)
        ec1 = (1, pend1, -pend1 * ptomd1[0] + ptomd1[1])
        ec2 = (1, pend2, -pend2 * ptomd2[0] + ptomd2[1])
        '''
        #Se realizan los nuevos calculos
        if y2 - y1 == 0:
            pend1 = 0
        else:
            pend1 = - ((x2 - x1) / (y2 - y1))
            print pend1
        if y2 - y3 == 0:
            pend2 = 0
        else:
            pend2 = -(x2 - x3) / (y2 - y3)

        ptomcercano = ptomd1 if math.sqrt(math.pow(x2 - ptomd1[0], 2) + math.pow(y2 - ptomd1[1], 2)) \
                                < math.sqrt(math.pow(x2 - ptomd2[0], 2) + math.pow(y2 - ptomd2[1], 2)) else ptomd2
        ptomenoscercano = ptomd2 if math.sqrt(math.pow(x2 - ptomd1[0], 2) + math.pow(y2 - ptomd1[1], 2)) \
                                    < math.sqrt(math.pow(x2 - ptomd2[0], 2) + math.pow(y2 - ptomd2[1], 2)) else ptomd1
        pendiente = pend1 if ptomcercano == ptomd1 else pend2
        print "El punto mas cercano es : " + str(ptomcercano)

        # Ax + By + C = 0  ==> (A,B,C)
        #primec = (y2 - y1, -(x2 - x1), (y2 - y1) * x1 - y1 * (x2 - x1))
        #segundaec = (y3 - y2, -(x3 - x2), (y3 - y2) * x3 - y2 * (x3 - x2))

        primec = (y2 - y1, -x2 + x1 , (y2 - y1) * x1 - y1 * (x2 - x1))
        segundaec = (y3 - y2, -x3 + x2, (y3 - y2) * x1 - y1 * (x3 - x2))

        raiz1 = math.sqrt(math.pow(primec[0], 2) + math.pow(primec[1], 2))
        raiz2 = math.sqrt(math.pow(segundaec[0], 2) + math.pow(segundaec[1], 2))
        # Calcular el punto medio mas cercano y usando dicho punto y el punto medio mas cercano
        # calcular las pendientes y  calcular las ecuaciones con puntos pendiente, exactamente lo hecho anterior
        # sustituyendo el punto mas lejano por el punto obtenido por medio de la bisectriz

        pendientebiz = -(raiz2 * primec[0] - raiz1 * segundaec[0]) / (raiz2 * primec[1] - raiz1 * segundaec[1])
        # Se calculan las ecuaciones puntopendiente :
        ec1 = (1, pendiente, -pendiente * ptomcercano[0] + ptomcercano[1])
        ec2 = (1, pendientebiz, -pendientebiz * x2 + y2)  # bisectriz
        # Se dibuvjan las recftas obtenidas de la ecuacion
        # k.create_line(0, ec1[2], 3000, 3000 * ec1[1] + ec1[2], fill="purple")
        # k.create_line(0, ec2[2], 3000, 3000 * ec2[1] + ec2[2], fill="blue")
        # Se igualan las y, se resuelve por x
        x = (ec2[2] - ec1[2]) / -(ec2[1] - ec1[1])
        y = x * ec1[1] + ec1[2]
        # print "Se intersectan en : " + str(x) + str(y)
        #k.create_rectangle(x,y,x+10,y+10, fill="gold")
        # (x,y) representa el centro del circulo
        r = math.sqrt(math.pow(x - ptomcercano[0], 2) + math.pow(y - ptomcercano[1], 2))
        r2 = math.sqrt(math.pow(x - ptomenoscercano[0], 2) + math.pow(y - ptomenoscercano[1], 2))
        # alfa = math.degrees(math.atan2((ptomd2[1] - y), (ptomd2[0] - x)))
        # beta = math.degrees(math.atan2((ptomd1[1] - y), (ptomd1[0] - x)))
        # DECENTE
        # alfa = math.degrees(math.atan2((ptomcercano[1] - y), (ptomcercano[0] - x)))
        # beta = math.degrees(math.atan2((ptomenoscercano[1] - y), (ptomenoscercano[0] - x)))
        # FINALIZA DECENTE
        alfa = math.degrees(math.atan2((ptomcercano[1] - y), (ptomcercano[0] - x)))
        beta = math.degrees(math.atan2((ptomenoscercano[1] - y), (ptomenoscercano[0] - x)))
        primpto = (x - r, y + r)
        segpto = (x - r, y - r)
        tercerpto = (x + r, y + r)
        crtopto = (x + r, y - r)
        print "r es : " + str(r)
        print "r2 es : " + str(r2)
        # Calcular las coordenadas del nuevo punto
        # Corregir coordenadas, deben ser la de los puntos medio
        #https://math.stackexchange.com/questions/361412/finding-the-angle-between-three-points
        #r = (r + r2) / 2

        radang.append((r, Mapa.aRobot(x1, y1,   (ptomd1[0]+ptomd2[0])/2 + r, (ptomd1[1]+ptomd2[1])/2 + r, x2, y2)))
        #k.create_line(x - r, y + r, x - r, y - r, fill="blue")
        #k.create_line(x - r, y + r, x + r, y + r, fill="blue")
        #k.create_line(x + r, y - r, x - r, y - r, fill="blue")
        #k.create_line(x + r, y - r, x + r, y + r, fill="blue")
        if beta < 0:
            beta = 360 + beta
        #while beta < 0.0:
         #   beta += math.pi * 2
        #while alfa < 0.0:
         #   alfa += math.pi * 2
        if alfa < 0:
            alfa = 360 + alfa
        return x - r, y + r, x + r, y - r, alfa, beta

    def calcula(self):
        self.nodos.append(Nodo(120, 120, []))  # NOdo Inicial
        self.nodos.append(Nodo(690, 500, []))  # Nodo Final
        k = Canvas(self.master, width=self.diccionario['longx'], height=self.diccionario['longy'])
        k.create_rectangle(120, 120, 130, 130, fill="red")  # Nodo Inicial
        k.create_rectangle(690, 500, 700, 510, fill="red")  # Nodo Final
        k.pack()
        # k.create_oval(0, 499, 0, 499, fill="red")
        # k.create_oval(499, 499, 499, 499, fill="red")
        genera = 500
        intentos = 0
        while genera > 0:
            intentos += 1
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
                    print "FALTAN : " + str(genera) + " PUNTOS"
                    self.nodos.append(Nodo(x, y, []))
        self.listaLineas = []
        print "HICE : " + str(intentos) + "intentos"
        # Para dibujar la linea entre los obstasculos
        for z in range(len(self.obstaculos)):
            for x in range(len(self.obstaculos[z])):
                for y in range(len(self.obstaculos[z])):
                    x0 = self.obstaculos[z][x][0]
                    y0 = self.obstaculos[z][x][1]
                    x1 = self.obstaculos[z][y][0]
                    y1 = self.obstaculos[z][y][1]

                    k.create_line(x0, y0, x1, y1, fill="red")
                    seEncuentra = False
                    for al in self.listaLineas:
                        arr = [al[0], al[1], al[2], al[3]]
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
                    # Distancias aceptables
                    if abs(x0 - x1) < 150 and abs(y0 - y1) < 150:
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

        #mainloop()


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
        return (self.coordx, self.coordy)

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __str__(self):
        return "(" + str(self.coordx) + " , " + str(self.coordy) + ")"

    def __repr__(self):
        return "(" + str(self.coordx) + " , " + str(self.coordy) + ")"

    def __hash__(self):
        return hash(self.__key())


class AEstrella:
    # Devolver False en caso de que no se haya encontrado solucion
    def __init__(self, inicio, meta, nodos=[]):
        self.inicio = inicio
        self.iinicioNB = NodoBusqueda(None, inicio)
        self.meta = meta
        self.metaNB = NodoBusqueda(None, meta)
        self.nodos = nodos
        self.listaAbierta = Queue.PriorityQueue()
        self.listaCerrada = {}
        self.solucion = []
        self.resuleto = False
        inicio.hn = AEstrella.calculaHeuristica(inicio, meta)
        self.nodoActual = None
        self.nodoPrevio = NodoBusqueda(None, inicio)
        self.listaAbierta.put(self.nodoPrevio)

    @staticmethod
    def calculaHeuristica(n1, n2):

        return math.hypot(n2.dameCoordenadax() - n1.dameCoordenadax(),
                          n2.dameCoordenaday() - n1.dameCoordenaday())

    def expandeNodoSiguiente(self):
        if self.resuleto:
            return
        self.nodoActual = self.listaAbierta.get()
        self.listaCerrada[self.nodoPrevio.estado] = self.nodoPrevio.estado
        self.nodoPrevio.estado.listaCerrada = True
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
                        sucesor.estado.hn = sucesor.calculaDistancia(self.meta) + NodoBusqueda.calculaAngulo(sucesor,
                                                                                                             self.metaNB)
                        sucesor.estado.gn = sucesor.gn + sucesor.calculaDistancia(
                            sucesor.padre.estado)  # Se agrega el costo dellegar al nodo
                        self.listaAbierta.put(sucesor)
                        sucesor.estado.listaCerrada = True
                else:
                    sucesor.estado.gn = sucesor.gn
                    sucesor.estado.padre = sucesor.padre.estado
        self.nodoPrevio = self.nodoActual


class NodoBusqueda:
    def __init__(self, padre, estado, m=1):
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
    def calculaAngulo(n1, n2):
        # Ver que acos siempre se ejecute
        # Si el nodo es el inicio  no hay angulo que calcular
        if n1.padre is None:
            return 1
        a = n1.padre.estado
        b = n1.estado
        c = n2.estado
        if a == c:  # El nodo intenta calcular el angulo de  a --- b --- a
            return 360
        ab = math.sqrt(math.pow(a.dameCoordenadax() - b.dameCoordenadax(), 2)
                       + math.pow(a.dameCoordenaday() - b.dameCoordenaday(), 2))
        bc = math.sqrt(math.pow(c.dameCoordenadax() - b.dameCoordenadax(), 2)
                       + math.pow(c.dameCoordenaday() - b.dameCoordenaday(), 2))
        ca = math.sqrt(math.pow(a.dameCoordenadax() - c.dameCoordenadax(), 2)
                       + math.pow(a.dameCoordenaday() - c.dameCoordenaday(), 2))

        numerador = math.pow(ab, 2) + math.pow(ca, 2) - math.pow(bc, 2)
        denominador = 2 * ab * ca
        if denominador == 0:
            return 0
        resultado = math.acos(numerador / denominador)
        return math.degrees(resultado)

    def getSucesores(self):
        sucesores = deque()
        for x in self.estado.dameAdyacentes():
            nodoSucesor = NodoBusqueda(self, x)
            dem = pow(NodoBusqueda.calculaAngulo(self, nodoSucesor), 2)
            if dem != 0:
                nodoSucesor.gn = self.gn + self.calculaDistancia(x) * (1 / dem) * self.m
            nodoSucesor.gn = 100000
            sucesores.append(nodoSucesor)
        return sucesores

    def __cmp__(self, nb1):
        return self.dameFn() - nb1.dameFn()

    def __repr__(self):
        return str(self.estado)


if __name__ == '__main__':

    obstaculos = [
                  [(0, 950), (0, 1000), (1300, 950), (1300, 1000)], #  CHECK
                  [(0, 0), (100, 0), (0, 1000), (100, 1000)], #  CHECK
                  [(1250, 0), (1300, 0), (1250, 950), (1250, 1000)], #CHECK
                  [(400, 250), (650, 250), (400, 650), (650, 650)],
                  [(850, 250), (850, 650), (1100, 250), (1100, 650)]
                  ]
    m1 = Mapa(1300, 1000, obstaculos)
    m1.calcula()
    alg = AEstrella(m1.nodos[0], m1.nodos[1], m1.nodos)
    num = 200
    while not alg.resuleto and num > 0:
        alg.expandeNodoSiguiente()
        num -= 1
    # Se dibujan las lineas del recorrido obtenido por A*
    # Se suavizan las lineas obtenidasd anteriormente
    # print alg.solucion[0]
    # print alg.solucion[-1]
    # master.after(ROS_RATE, exitros)
    # mainloop()
    print "la solucion es : "
    print alg.solucion
    master = Tk()
    k3 = Canvas(master, width=1300, height=1000)
    k3.pack()
    for x in range(len(alg.solucion)):
        k3.create_rectangle(alg.solucion[x].estado.dameCoordenadax(),
                            alg.solucion[x].estado.dameCoordenaday(),
                            alg.solucion[x].estado.dameCoordenadax() + 10,
                            alg.solucion[x].estado.dameCoordenaday() + 10, fill="red"
                            )
        # Para evitar hacer una linea de la meta al inicio
        if x != len(alg.solucion) - 1:
            k3.create_line(alg.solucion[x].estado.dameCoordenadax(),
                           alg.solucion[x].estado.dameCoordenaday(),
                           alg.solucion[(x + 1) % len(alg.solucion)].estado.dameCoordenadax(),
                           alg.solucion[(x + 1) % len(alg.solucion)].estado.dameCoordenaday(), fill="red")

    #mainloop()


    master = Tk()


    k3 = Canvas(master, width=1300, height=1000)
    k3.pack()
    #k3.create_rectangle(100, 120, 110, 130, fill="red")
    #k3.create_rectangle(200, 220, 210, 230, fill="red")
    #angulos = Mapa.calcula_arco(50 , 50, 100, 120, 200, 220)
    #k3.create_arc(100, 120, 200, 220,
     #            start=angulos[2], extent=angulos[3], style=tk.ARC, fill="green")
    #
    #k3.create_line(100, 120, 200, 220, fill ="orange")

    m1.suaviza(alg.solucion, k3)
    mainloop()
    print radang
## Cosas de ROS
# https://www.ethz.ch/content/dam/ethz/special-interest/mavt/robotics-n-intelligent-systems/rsl-dam/ROS2017/lecture1.pdf