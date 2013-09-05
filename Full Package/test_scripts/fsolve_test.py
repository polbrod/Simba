# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 23:22:48 2013

@author: Nathan
"""
from scipy import optimize as opt

speed = 20
d = 10
a = .5
alt1 = 30
alt2 = 20
dist1 = 10 
dist2 = 0
mass = 100
g = 9.8
h = .1
top_force = 50
def force_solve(s):
    return Force(s) - top_force

def Force(s):
    a = (s - speed)/h
    drag = 0.5 * d*a*s**2
    slope = (alt1 - alt2)/(dist1 - dist2)    
    incline = mass*g*slope
    return a + drag + incline
    
    
print(opt.fsolve(force_solve,30))[0]