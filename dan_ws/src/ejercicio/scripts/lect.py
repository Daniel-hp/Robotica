from __future__ import print_function
import serial

ser = serial.Serial(
    port='COM4',\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)
count=10000
nombre = raw_input("Dame el nombre del archivo con extension\n")
f = open(nombre, "w")
## Hacer que quede de la siguiente manera
'''
Distancias Mediciones
10          
20          
30          
40              
50          
.

Angulos Mediciones
10
20
30
40
50
'''
while count > 0:
    for line in ser.read():
        x = "\n" if line is "," else ""
        line = str(line) if line is not "," else ""
        print(line, end=x, file=f)
        count -= 1

f.close()
ser.close()
