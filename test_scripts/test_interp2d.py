# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 18:41:47 2013

@author: Nathan
"""

from scipy.interpolate import interp2d
from scipy import optimize as opt
from scipy.interpolate import UnivariateSpline,interp1d
import math 
import numpy as np
import itertools
import collections
import logging

x = np.array([0, 1, 2,3])
y = np.array([0, 1, 2,3])
z = np.array([0,1,2,3])
f = interp2d(x, y, z, kind='linear')