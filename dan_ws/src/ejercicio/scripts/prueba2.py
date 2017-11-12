from Tkinter import *
import math
import Tkinter as tk
def calculaCirculo(x1, y1, x2, y2, x3, y3, k):
        ptomd1 = ((x1 + x2) / 2, (y1 + y2) / 2)
        ptomd2 = ((x2 + x3) / 2, (y2 + y3) / 2)
        k.create_rectangle(x1, y1, x1 + 10, y1 + 10, fill="green")
        k.create_rectangle(x2, y2, x2 + 10, y2 + 10, fill="green")
        k.create_rectangle(x3, y3, x3 + 10, y3 + 10, fill="green")
        k.create_rectangle(ptomd1[0], ptomd1[1], ptomd1[0] + 10, ptomd1[1] + 10)
        k.create_rectangle(ptomd2[0], ptomd2[1], ptomd2[0] + 10, ptomd2[1] + 10)
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
        #k.create_line(x - r, y + r, x - r, y - r, fill="blue")
        #k.create_line(x - r, y + r, x + r, y + r, fill="blue")
        #k.create_line(x + r, y - r, x - r, y - r, fill="blue")
        #k.create_line(x + r, y - r, x + r, y + r, fill="blue")
        if beta < 0:
            beta = 360 + beta
        if alfa < 0:
            alfa = 360 + alfa
        return x - r, y + r, x + r, y - r, alfa, beta
master = Tk()
k = Canvas(master, width=1000, height=1000)
k.pack()

'''
Se tiene de la siguiente manera :

           
      A    |    B
           |
           |
     ______|______
           |
           |
     C     |    D
'''
k.create_rectangle(150, 150, 160, 160, fill="red") # CENTRO
k.create_rectangle(100, 100, 110, 110, fill="green") # A
k.create_rectangle(200, 200, 210, 210, fill="blue") # D
k.create_rectangle(200, 100, 210, 110, fill="purple") # B
k.create_rectangle(100,200,110,210, fill="cyan") # C

# Se hacen las lineas
#k.create_line(100, 100, 200, 100) # A B
#k.create_line(200, 100, 100, 200) # B C
#k.create_line(100, 200, 200, 200) # C D
#k.create_line(100, 100, 100, 200) # A C
#k.create_line(200, 100, 200, 200) # B D
#k.create_line(100, 100, 200, 200) # A D

#angulos = calculaCirculo(100, 200, 100, 100, 200, 100, k) # Se calcula el circulo de C A B ## Deberia ir al reves
angulos = calculaCirculo(100, 200, 100, 100, 200, 100, k) # Se calcula el circulo de C A B
#angulos = calculaCirculo(100, 200, 100, 100, 200, 100, k) # Se calcula el circulo de C A B
#angulos = calculaCirculo(100, 200, 100, 100, 200, 100, k) # Se calcula el circulo de C A B
#angulos = calculaCirculo(100, 200, 100, 100, 200, 100, k) # Se calcula el circulo de C A B
#angulos = calculaCirculo(100, 200, 100, 100, 200, 100, k) # Se calcula el circulo de C A B
#angulos = calculaCirculo(100, 200, 100, 100, 200, 100, k) # Se calcula el circulo de C A B
#print angulos
k.create_arc(angulos[0], angulos[1], angulos[2], angulos[3],start=-angulos[5], extent=angulos[5] - angulos[4], style=tk.ARC, fill="green")
k.mainloop()
