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
