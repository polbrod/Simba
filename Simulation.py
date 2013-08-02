# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 22:43:03 2013

@author: Nathan
"""

from scipy import optimize as opt
from scipy.interpolate import UnivariateSpline,interp1d
import math 
import numpy as np
import itertools

#Tests

    #condition = [1,2,3]                  #example test

    #tests = size(condition)              #right formula for number of test

tests = 1
#Variables

h = 0.1                               #time step in seconds
total_time = 60*60                      #total time (used to calc array size)
steps = int(math.ceil(total_time/h))

#constants 
top_speed = 62
top_force = 1500
drag_area = 1.5
air_density = 1.1839
mass = 310
gravity = 9.8
max_distance = 60350

#Arrays
time = np.zeros((steps+1,tests),dtype=float)
distance = np.zeros((steps+1,tests),dtype=float)
l_speed = np.zeros((steps+1,tests),dtype=float)
t_speed = np.zeros((steps+1,tests),dtype=float)
c_force = np.zeros((steps+1,tests),dtype=float)
speed = np.zeros((steps+1,tests),dtype=float)
force = np.zeros((steps+1,tests),dtype=float)
power = np.zeros((steps+1,tests),dtype=float)
energy = np.zeros((steps+1,tests),dtype=float)
acceleration = np.zeros((steps+1,tests),dtype=float)
drag = np.zeros((steps+1,tests),dtype=float)
altitude = np.zeros((steps+1,tests),dtype=float)
slope = np.zeros((steps+1,tests),dtype=float)
incline = np.zeros((steps+1,tests),dtype=float)

#Lookups
n = np.loadtxt('disttospeed.csv',dtype = 'string',delimiter = ';', skiprows = 1)
x = n[:,0].astype(np.float) * 1609.34
y = n[:,1].astype(np.float)
distancetospeed_lookup = interp1d(x,y)

n = np.loadtxt('disttoalt.csv',dtype = 'string',delimiter = ',', skiprows = 1)
x = n[:,0].astype(np.float) * 1000
y = n[:,1].astype(np.float)
distancetoaltitude_lookup = interp1d(x,y)

#functions
def force_solve(s,n):
    return Force(s,n) - top_force

def Force(s,n):
    acceleration[n+1] = (s - speed[n])/h
    drag[n+1] = 0.5 * drag_area*air_density*s**2
    altitude[n+1] = distancetoaltitude_lookup(distance[n+1])
    slope[n+1] = (altitude[n+1] - altitude[n])/(distance[n+1] - distance[n])    
    incline[n+1] = mass*gravity*slope[n+1]
    return acceleration[n+1] + drag[n+1] + incline[n+1]


#initial condidtions
distance[0] = .1
speed[0] = .1
altitude[0] = distancetoaltitude_lookup(1)

#simulation and plot loop
#(iteration,test conditions..) 
def loop(n):
    end = steps
    for n in range(steps):
        #model formulas here
        time[n+1] = time[n] + h
        distance[n+1] = distance[n] + speed[n]*h
        if (distance[n+1] > max_distance):
            end = n
            break
        l_speed[n+1] = distancetospeed_lookup(distance[n+1])
        
        if l_speed[n+1] > top_speed:
            t_speed[n+1] = top_speed
        else:
            t_speed[n+1] = l_speed[n+1]
            
        
        c_force[n+1] = Force(t_speed[n+1],n)
        
        if c_force[n+1] > top_force:
            speed[n+1] = (opt.fsolve(force_solve,t_speed[n+1],n))[0]
            force[n+1] = top_force
        else:
            speed[n+1] = t_speed[n+1]
            force[n+1] = c_force[n+1]
        
        power[n+1] = force[n+1] * speed[n+1]
        energy[n+1] = energy[n] + power[n+1]*(h/(60*60))
                    
   #plot each loop here


   
#simulate and plot

n = 0
#for c  in condition:
loop(n)
n+=1
    
#finish plot

    