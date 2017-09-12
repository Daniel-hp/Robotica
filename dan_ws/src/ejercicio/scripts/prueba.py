#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from Tkinter import *
from random import randint
from collections import deque
import Queue
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

    def dibuja(self):
        k = Canvas(self.master, width=self.diccionario['longx'], height=self.diccionario['longy'])
        k.pack()
        genera = 200
        while genera > 0:
            entro = False
            x = randint(0,self.diccionario['longx'])
            y = randint(0,self.diccionario['longx'])

            # Verifica no exista el nodo ya en la lista
            for z in range(len(self.nodos)):
                a = Nodo(x,y,[])

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
        lista_lineas=[]
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
                        for al in lista_lineas:
                            arr = [int(k.coords(al)[0]),int(k.coords(al)[1]),int(k.coords(al)[2]),int(k.coords(al)[3])]
                            if arr == [x1,y1,x0,y0]:
                                seEncuentra = True
                        if not seEncuentra:
                            alfa = k.create_line(x0, y0, x1, y1, fill="red" )
                            lista_lineas.append(alfa)
        # Para dibujar la linea entre los puntos verificando estas no choquen y
        for x in range(len(self.nodos)):
            for y in range(len(self.nodos)):
                if self.nodos[x] != self.nodos[y]:
                    x0 = self.nodos[x].coordx
                    y0 = self.nodos[x].coordy
                    x1 = self.nodos[y].coordx
                    y1 = self.nodos[y].coordy
                    if abs(x0 - x1) < 80 and abs(y0 - y1) < 80:
                        bool = True
                        for z in lista_lineas:
                            alfa = k.coords(z)
                            if Mapa.interseccion(x0, y0, x1, y1, alfa[0], alfa[1], alfa[2], alfa[3]):
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


    def __repr__(self):
        return "Coordenada x" + str(self.coordx) + " Coordenada y" + str(self.coordy) \
               + " Adyacentes: " + "".join([str(i) for i in self.listaAdyacentes])
    def __hash__(self):
        return hash(self.__key())

class AEstrella:
    def __init__(self,inicio,meta, nodos = []):
        self.inicio = inicio
        self.meta = meta
        self.nodos = nodos
        self.listaAbierta = Queue.PriorityQueue()
        self.listaCerrada = {}
        self.resuleto = False
        inicio.hn = AEstrella.calculaHeuristica(inicio,meta)
        self.listaAbierta.put(inicio)

    @staticmethod
    def calculaHeuristica(n1,n2):
        return math.hypot(n2.dameCoordenadax - n1.dameCoordenadax,
                          n2.dameCoordenaday - n1.dameCoordenaday)

    def expandeNodoSiguiente(self):
        if self.resuleto:
            return
        nodoActual = self.listaAbierta.get()
        self.listaCerrada[nodoActual.estado] = nodoActual.estado
        if nodoActual.estado == self.meta
            self.resuleto = True
            tmp = nodoActual
            while tmp.estado != self.inicio:
                tmp.estado.sol = True
                tmp = tmp.padre
        else:
            suc = nodoActual.getSucesores()
            for sucesor in suc:
                if not sucesor.estado.listaCerrada:
                    if not sucesor.estado.listaAbierta:
                        sucesor.estado.calculaHeuristica()
                        sucesor.estado.gn = sucesor.gn
 // implementar offer


class NodoBusqueda:
    def __init__(self, padre,estado, gn):
        self.padre = padre
        self.estado = estado
        self.gn = gn

    def dameFn(self):
        estado.damehn() + self.gn

    def calculaDistancia(self, n1):
        return math.hypot(self.estado.dameCoordenadax - n1.dameCoordenadax,
                          self.estado.dameCoordenaday - n1.dameCoordenaday)

    def getSucesores(self):
        sucesores = deque()
        for x in estado.dameAdyacentes():
            nodoSucesor = NodoBusqueda(self,x,self.gn + self.calculaDistancia(x))
            sucesores.append(nodoSucesor)
        return sucesores

    def compara(self,nb1):
        return self.dameFn() - nb1.dameFn()


if __name__ == '__main__':
    m1 = Mapa(500,500,[[(0,0),(150,200),(300,110)]])
    m1.dibuja()