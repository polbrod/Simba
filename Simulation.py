# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 22:43:03 2013

@author: Nathan
"""

import Lookup
from scipy import optimize as opt
import math 
import numpy as np
import itertools

#Tests

    #condition = [1,2,3]                  #example test

    #tests = size(condition)              #right formula for number of test

tests = 1
#Variables

h = 1.0                               #time step in seconds
total_time = 60*60                      #total time (used to calc array size)
steps = int(math.ceil(total_time/h))

#constants 


#Arrays

T = np.zeros((steps+1,tests),dtype=float) #example array

#Lookups


#functions
def force_solve(s):
    return force(s) - top_force

def Force(s):
    acceleration[n+1] = (s - speed[n])/h
    drag[n+1] = 0.5 * drag_area*air_density*s**2
    altitude[n+1] = distancetoaltitude_lookup(distance[n+1])
    slope[n+1] = (altitude[n+1] - altitude[n])/(distance[n+1] - distance[n])    
    incline[n+1] = mass*gravity*slope[n+1]
    return acceleration[n+1] + drag[n+1] + incline[n+1]


#initial condidtions


#simulation and plot loop
#(iteration,test conditions..) 
def loop(n,c):
    end = steps
    for s in range(steps):
        
        #model formulas here
        time[n+1] = time[n] + h
        distance[n+1] = distance[n] + speed[n]*h
        l_speed[n+1] = distancetospeed_lookup(dist[n+1])
        
        if l_speed[n+1] > top_speed:
            t_speed[n+1] = top_speed
        
        c_force[n+1] = Force(t_speed[n+1])
        
        if c_force[n+1] > top_force:
            speed[n+1] = (opt.fsolve(force_solve,t_speed))(0)
            force[n+1] = top_force
        else:
            speed[n+1] = t_speed[n+1]
            force[n+1] = c_force[n+1]
        
        power[n+1] = force[n+1] * speed[n+1]
        energy[n+1] = energy[n] + power[n+1]*h
                    
   #plot each loop here


   
#simulate and plot

n = 0
#for c  in condition:
    loop(n,c)
    n+=1
    
#finish plot

    