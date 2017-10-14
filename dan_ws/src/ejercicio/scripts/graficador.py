from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

'''
info
https://stackoverflow.com/questions/35210337/can-i-plot-several-histograms-in-3d

'''
#filename = "datos.txt"
#data = []
#data = data + [np.loadtxt(filename)]
data = [[] for _ in range(6)]
data[0] =np.loadtxt("primeramedicion.txt")
data[1] =np.loadtxt("segundamedicion.txt")
data[2] =np.loadtxt("terceramedicion.txt")
data[3] =np.loadtxt("cuartamedicion.txt")
data[4] =np.loadtxt("quintamedicion.txt")
data[5] =np.loadtxt("sextamedicion.txt")

#data =[[1,2,3,4],[20,24,33,12], [12,45,21,32],[10,20,100,50],
 #      [1, 2, 3, 4], [20, 24, 33, 12], [12, 45, 21, 32], [10, 20, 100, 50],
  #     [1, 2, 3, 4], [20, 24, 33, 12], [12, 45, 21, 32], [10, 20, 100, 50],
   #    [1, 2, 3, 4], [20, 24, 33, 12], [12, 45, 21, 32], [10, 20, 100, 50],
    #   [1, 2, 3, 4], [20, 24, 33, 12], [12, 45, 21, 32], [10, 20, 100, 50]]
fig = plt.figure(figsize=(100,100))
ax = fig.add_subplot(111, projection='3d')
nbins = 300
#for c, z in zip(['r', 'g', 'b', 'y'], [30, 20, 10, 0]):
for x,y,z in zip(range(len(data)),[0,10,20,30,40,50,60],['r','g','b','y','r','g']):
    #print np.random.normal(loc=10, scale=10, size=2000)
    ys = data[x]
    hist, bins = np.histogram(ys, bins=nbins)
    xs = (bins[:-1] + bins[1:])/2
    ax.bar(xs, hist, zs=y, zdir='y', color=z, ec=z, alpha=1)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()

