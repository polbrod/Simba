# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 18:41:47 2013

@author: Nathan
"""

''' working example

must change lookup to correct path '''

from scipy.interpolate import griddata
from scipy import optimize as opt
from scipy.interpolate import UnivariateSpline,interp1d
import math 
import numpy as np
import itertools
import collections
import logging


lookup = "C:\\Users\\Nathan\\Desktop\\CAR sync\\Buckeye_Current\\python\\bike_optimization\\test_in\\Lookup Files\\Tritium_ws200_eff.csv"

n = np.loadtxt(lookup,dtype = 'string',delimiter = ',', skiprows = 1)
x = n[:,0].astype(np.float)
y = n[:,1].astype(np.float)
z = n[:,2].astype(np.float)

points = np.transpose(np.array([x,y]))
values = np.array(z)

grid_x, grid_y = np.mgrid[np.min(x):np.max(x), np.min(y):np.max(y)]

grid = griddata(points, values, (grid_x, grid_y), method='linear')