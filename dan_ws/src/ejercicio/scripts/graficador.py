from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

'''
info
https://stackoverflow.com/questions/35210337/can-i-plot-several-histograms-in-3d

'''
filename = "datos.txt"
Data = np.loadtxt(filename)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
nbins = 100
for c, z in zip(['r', 'g', 'b', 'y'], [30, 20, 10, 0]):
    #ys = np.random.normal(loc=10, scale=10, size=2000)
    ys = [.5,.4,.1,.005,.8,.12,1]
    hist, bins = np.histogram(ys, bins=nbins)
    xs = (bins[:-1] + bins[1:])/2

    ax.bar(xs, hist, zs=z, zdir='y', color=c, ec=c, alpha=0.8)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.show()
print Data
