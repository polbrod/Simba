# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 18:41:47 2013

@author: Nathan
"""
import matplotlib.pyplot as plt
from scipy.interpolate import SmoothBivariateSpline
from scipy import optimize as opt
from scipy.interpolate import UnivariateSpline,interp1d
import math 
import numpy as np
import itertools
import collections
import logging


lookup = "C:\\Users\\Nathan\\Desktop\\CAR sync\\Buckeye_Current\\python\\bike_optimization\\test_in\\Lookup Files\\Emrax_eff.csv"

n = np.loadtxt(lookup,dtype = 'string',delimiter = ',', skiprows = 1)
x = n[:,0].astype(np.float)
y = n[:,1].astype(np.float)
z = n[:,2].astype(np.float)
f = SmoothBivariateSpline(x, y, z)

xnew = np.arange(0, 5000, 20)
ynew = np.arange(0,250)
znew = f(xnew, ynew)
plt.plot(x, z, 'ro-', xnew, znew[:, 0], 'b-')
plt.show()