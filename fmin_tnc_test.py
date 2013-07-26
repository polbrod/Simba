# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 23:22:48 2013

@author: Nathan
"""
from scipy import optimize as opt

def f((a,b,c,d)):
    return a*b - c*d
    

x0 = [1,1,3,4]
bound = [(0,10),(-1,5),(-10,-3),(-5,-1)]
print(opt.minimize(f,x0,bounds = bound,method = 'TNC'))