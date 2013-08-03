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


tests = 1
#parameters

step = 0.1           #time step in seconds
total_time = 60*60
wheel_radius = 0.323596 #meters
gearing = 2.174
rider_mass = 81.64 #kg
bike_mass = 192.695 #kg
gravity = 9.81
air_resistance = 0.7
air_density = 1.204
frontal_area =  0.7 #m^2
rolling_resistance = 0.022
top_torque = 200 #nm
top_rpm = 5000
efficiency = 1.0925
max_distance_travel = 60350 #meters this needs to be calculated from lookups

dist_to_speed_lookup = 'disttospeed.csv'
dist_to_alt_lookup = 'disttoalt.csv'

#calc values
top_speed = ((wheel_radius*2*np.pi* (top_rpm) / (gearing))/60)
top_force = (top_torque * gearing) / wheel_radius
drag_area = frontal_area * air_resistance
mass = rider_mass + bike_mass
steps = int(math.ceil(total_time/step))

#Arrays (output)
time = np.zeros((steps+1,tests),dtype=float)
distance = np.zeros((steps+1,tests),dtype=float)
l_speed = np.zeros((steps+1,tests),dtype=float) #look up speed
t_speed = np.zeros((steps+1,tests),dtype=float) #speed after compare to top
c_force = np.zeros((steps+1,tests),dtype=float) #force before compare
speed = np.zeros((steps+1,tests),dtype=float)   #speed after compare (actual)
force = np.zeros((steps+1,tests),dtype=float)   #force after compare (actual)
power = np.zeros((steps+1,tests),dtype=float)
energy = np.zeros((steps+1,tests),dtype=float)
acceleration = np.zeros((steps+1,tests),dtype=float)
drag = np.zeros((steps+1,tests),dtype=float)
altitude = np.zeros((steps+1,tests),dtype=float)
slope = np.zeros((steps+1,tests),dtype=float)
incline = np.zeros((steps+1,tests),dtype=float)
rolling = np.zeros((steps+1,tests),dtype=float)

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
    acceleration[n+1] = (s - speed[n])/step
    drag[n+1] = 0.5 * drag_area*air_density*s**2
    altitude[n+1] = distancetoaltitude_lookup(distance[n+1])
    slope[n+1] = (altitude[n+1] - altitude[n])/(distance[n+1] - distance[n])    
    incline[n+1] = mass*gravity*slope[n+1]
    rolling[n+1] = mass*gravity*rolling_resistance
    return acceleration[n+1] + drag[n+1] + incline[n+1]


#initial condidtions
distance[0] = .1
speed[0] = .1
altitude[0] = distancetoaltitude_lookup(1)

#simulation and plot loop
#(iteration,test conditions..) 
def loop(n):
    for n in range(steps):
        #model formulas here
        time[n+1] = time[n] + step
        distance[n+1] = distance[n] + speed[n]*step
        if (distance[n+1] > max_distance_travel):
            return n
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
        
        power[n+1] = (force[n+1] * speed[n+1])/efficiency
        energy[n+1] = energy[n] + power[n+1]*(step/(60*60))
        
    return steps
   #plot each loop here


   
#simulate and plot

n = 0
#for c  in condition:
end = loop(n)
n+=1

print 'average mph = ' + repr(np.mean(speed[:end])*2.23)
print 'average power = ' + repr(np.mean(power[:end]))
print 'max power = ' + repr(np.max(power[:end]))
print 'energy = ' + repr(np.max(energy))

#finish plot

    