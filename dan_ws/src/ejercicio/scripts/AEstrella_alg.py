import Queue
import math
from collections import deque

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
