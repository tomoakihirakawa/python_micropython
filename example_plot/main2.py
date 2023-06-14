# from __future__ import print_function
import matplotlib.pyplot as plt
from math import sin

def tranpose(matIN):    
    return [[matIN[j][i] for j in range(len(matIN))] for i in range(len(matIN[0]))]

def linspace(s,e,n):
    d = (e-s)/(n-1)
    return [s+d*i for i in range(n)]

def Dot(v,u):
    ret = 0
    for i in range(len(v)):
        ret += v[i]*u[i]        
    return ret

# -------------------- shape functions ------------------- #

def shapeLin(t0,t1):
    return [t0,t1,1-t0-t1]

def shapeQuad(t0,t1):
    t2 = 1 - t0 - t1
    return [t0*(2*t0-1),
            t1*(2*t1-1),
            t2*(2*t2-1),
            4*t0*t1,
            4*t1*t2,
            4*t0*t2]

def shapeCubic(t0,t1):
    t2 = 1 - t0 - t1
    return [t0/2*(3*t0-1)*(3*t0-2),
            t1/2*(3*t1-1)*(3*t1-2),
            t2/2*(3*t2-1)*(3*t2-2),
            9/2*t0*t1*(3*t0-1),
            9/2*t1*t0*(3*t1-1),
            9/2*t1*t2*(3*t1-1),
            9/2*t2*t1*(3*t2-1),
            9/2*t2*t0*(3*t2-1),
            9/2*t0*t2*(3*t0-1),
            27*t0*t1*t2]

# ---------------------- plot figure --------------------- #

import numpy as np
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D


sample3=[[0,0,0],[2,0,2],[1,2,1]]
ps=[[2/3,0,0],
    [5/3,2/3,1],
    [2/3,4/3,0]]
sample6=sample3+ps

ps=[[2/3,0,0],[4/3,0,0],
    [5/3,2/3,1],[4/3,4/3,1],
    [2/3,4/3,0],[2/3,2/3,0],
    [1,1,1]]

sample10=sample3+ps

sample3T = tranpose(sample3)
sample6T = tranpose(sample6)
sample10T = tranpose(sample10)
# -------------------------------------------------------- #
X3=[]
Y3=[]
Z3=[]

X6=[]
Y6=[]
Z6=[]

X10=[]
Y10=[]
Z10=[]
for i in linspace(0,1,20):
    for j in linspace(0,1-i,20):
        # ------------------------ linear ------------------------ #
        X3.append(Dot(sample3T[0],shapeLin(i,j)))
        Y3.append(Dot(sample3T[1],shapeLin(i,j)))        
        Z3.append(Dot(sample3T[2],shapeLin(i,j)))
        # ------------------------- quad ------------------------- #
        X6.append(Dot(sample6T[0],shapeQuad(i,j)))
        Y6.append(Dot(sample6T[1],shapeQuad(i,j)))        
        Z6.append(Dot(sample6T[2],shapeQuad(i,j)))
        # ------------------------- cubic ------------------------ #
        X10.append(Dot(sample10T[0],shapeCubic(i,j)))
        Y10.append(Dot(sample10T[1],shapeCubic(i,j)))        
        Z10.append(Dot(sample10T[2],shapeCubic(i,j)))

X3=np.array(X3)
Y3=np.array(Y3)
Z3=np.array(Z3)

X6=np.array(X6)
Y6=np.array(Y6)
Z6=np.array(Z6)

X10=np.array(X10)
Y10=np.array(Y10)
Z10=np.array(Z10)
# -------------------------------------------------------- #
fig = plt.figure()
ax1 = fig.add_subplot(131,projection='3d')
ax2 = fig.add_subplot(132,projection='3d')
ax3 = fig.add_subplot(133,projection='3d')

ax1.scatter(X3, Y3, Z3)
ax1.scatter(np.array(sample3T[0]), np.array(sample3T[1]), np.array(sample3T[2]))

ax2.scatter(X6, Y6, Z6)
ax2.scatter(np.array(sample6T[0]), np.array(sample6T[1]), np.array(sample6T[2]))

ax3.scatter(X10, Y10, Z10)
ax3.scatter(np.array(sample10T[0]), np.array(sample10T[1]), np.array(sample10T[2]))
plt.show()




















