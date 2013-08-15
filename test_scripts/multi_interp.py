# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 18:41:47 2013

@author: Nathan
"""

from scipy.interpolate import griddata
from scipy import optimize as opt
from scipy.interpolate import UnivariateSpline,interp1d
import math 
import numpy as np
import itertools
import collections
import logging

points = np.array([[0,0],[1,1],[2,2])
values = np.array([0,1,2])

grid_x, grid_y = np.mgrid[0:2, 0:2]

grid = griddata(points, values, (grid_x, grid_y), method='nearest')