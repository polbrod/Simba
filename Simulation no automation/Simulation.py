# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 22:43:03 2013

@author: Nathan
"""

from scipy import optimize as opt
from scipy.interpolate import griddata,interp1d
import math 
import numpy as np
import itertools


tests = 1
#parameters

step = .1       #time step in seconds
total_time = 60*30
wheel_radius = 0.323596 #meters
gearing = 2.1
rider_mass = 81.64 #kg
bike_mass = 226.7 #kg
gravity = 9.81
air_resistance = 0.7
air_density = 1.204
frontal_area =  0.7 #m^2
rolling_resistance = 0.0187
top_torque = 500 #nm
top_rpm = 6000
#efficiency = 0.8075


#simulation calcs
steps = int(math.ceil(total_time/step))
sqrt2 = np.sqrt(2)

max_distance_travel = 60600 #meters this needs to be calculated from lookups
#max_distance_travel = 3218.69
dist_to_speed_lookup = 'iom_data.csv'
dist_to_alt_lookup = 'disttoalt.csv'

motor_controller_eff_lookup = 'Tritium_ws200_eff.csv'
motor_eff_lookup = 'Emrax_eff.csv'
chain_efficiency = .98
battery_efficiency = .98
motor_torque_constant = 1   #torque to current constant of motor. torque/amp
motor_rpm_constant = 12     #rpm to voltage dc constant of motor. rpm/volt



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

motor_rpm = np.zeros((steps+1,tests),dtype=float)
motor_torque = np.zeros((steps+1,tests),dtype=float)
motor_loss = np.zeros((steps+1,tests),dtype=float)
motor_controller_loss = np.zeros((steps+1,tests),dtype=float)
chain_loss = np.zeros((steps+1,tests),dtype=float)
battery_loss = np.zeros((steps+1,tests),dtype=float)
total_power = np.zeros((steps+1,tests),dtype=float) #power with losses
arms = np.zeros((steps+1,tests),dtype=float)    #amps rms out from motor controller
vrms = np.zeros((steps+1,tests),dtype=float)    #voltage rms out from motor controller

#Lookups
n = np.loadtxt(dist_to_speed_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
x = n[:,0].astype(np.float)
y = n[:,1].astype(np.float)
#x = np.array([0,3220])
#y = np.array([1000,1000])
distancetospeed_lookup = interp1d(x,y)

n = np.loadtxt(dist_to_alt_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
x = n[:,0].astype(np.float)
y = n[:,1].astype(np.float)
#x = np.array([0,3220])
#y = np.array([0,0])
distancetoaltitude_lookup = interp1d(x,y)

n = np.loadtxt(motor_controller_eff_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
x = n[:,0].astype(np.float)
y = n[:,1].astype(np.float)
z = n[:,2].astype(np.float)
points = np.transpose(np.array([x,y]))
values = np.array(z)
grid_x, grid_y = np.mgrid[np.min(x):np.max(x)+1, np.min(y):np.max(y)+1]
motor_controller_eff_grid = griddata(points, values, (grid_x, grid_y), method='linear')
#[volts_rms][amps_rms]
n = np.loadtxt(motor_eff_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
x = n[:,0].astype(np.float)
y = n[:,1].astype(np.float)
z = n[:,2].astype(np.float)
points = np.transpose(np.array([x,y]))
values = np.array(z)
grid_x, grid_y = np.mgrid[np.min(x):np.max(x)+1, np.min(y):np.max(y)+1]
motor_eff_grid = griddata(points, values, (grid_x, grid_y), method='linear')
#[rpm][torque]

#look up tests

if np.max(distancetospeed_lookup.x) < max_distance_travel:
    max_distance_travel =  np.max(distancetospeed_lookup.x)  
    print 'max_distance_travel greater than speed to distance look up'
    print 'max_distance_travel changed to ' + repr(max_distance_travel)


if np.max(distancetoaltitude_lookup.x) < max_distance_travel:
    max_distance_travel =  np.max(distancetoaltitude_lookup.x)  
    print 'max_distance_travel greater than altitude to distance look up'
    print 'max_distance_travel changed to ' + repr(max_distance_travel)

(x,y) = motor_eff_grid.shape
if y-1 <  top_torque:
    top_torque = y-1
    print 'top_torque greater than motor efficiency look up'
    print 'top_torque changed to ' + repr(top_torque)

if x-1 <  top_rpm:
    top_rpm = x-1
    print 'top_rpm greater than motor efficiency look up'
    print 'top_rpm changed to ' + repr(top_rpm)

(x,y) = motor_controller_eff_grid.shape
if y-1 <  top_torque/motor_torque_constant:
    top_torque = (y-1) * motor_torque_constant
    print 'possible arms (from top_torque and motor torque constant) is greater than motor controller efficiency look up'
    print 'top_torque changed to ' + repr(top_torque)

if x-1 <  (top_rpm/(motor_rpm_constant)*(1/(sqrt2))) :
    top_rpm = (x-1)*(motor_rpm_constant)*(1/(sqrt2)) 
    print 'possible Vrms (from top_rpm and motor rpm constant) is greater than motor controller efficiency look up'
    print 'top_rpm changed to ' + repr(top_rpm)
    
#functions
def force_solve(s,n):
    return Force(s,n) - top_force

def Force(s,n):
    acceleration[n+1] = mass*((s - speed[n])/step)
    drag[n+1] = 0.5 * drag_area*air_density*s**2
    altitude[n+1] = distancetoaltitude_lookup(distance[n+1])
    slope[n+1] = (altitude[n+1] - altitude[n])/(distance[n+1] - distance[n])    
    incline[n+1] = mass*gravity*slope[n+1]
    rolling[n+1] = mass*gravity*rolling_resistance
    return acceleration[n+1] + drag[n+1] + incline[n+1] + rolling[n+1]

def Efficiency(n):
    motor_rpm[n+1] = ((speed[n+1])/(wheel_radius*2*np.pi)) * gearing * 60
    motor_torque[n+1] = (force[n+1] * wheel_radius)/gearing
    arms[n+1] = motor_torque[n+1]/motor_torque_constant
    vrms[n+1] = motor_rpm[n+1]/(motor_rpm_constant)*(1/(sqrt2))           
     
    motor_loss[n+1] = power[n+1]*(1-motor_eff_grid[np.int(np.around(motor_rpm[n+1]))][np.int(np.around(motor_torque[n+1]))])
    motor_controller_loss[n+1] = power[n+1]*(1-motor_controller_eff_grid[np.int(np.around(vrms[n+1]))][np.int(np.around(arms[n+1]))])
    chain_loss[n+1] = power[n+1]*(1-chain_efficiency)
    battery_loss[n+1] = power[n+1]*(1-battery_efficiency)
    return motor_loss[n+1] + motor_controller_loss[n+1] + chain_loss[n+1] + battery_loss[n+1]
      
      
#parameter calc values
top_speed = ((wheel_radius*2*np.pi* (top_rpm) / (gearing))/60)
top_force = (top_torque * gearing) / wheel_radius
drag_area = frontal_area * air_resistance
mass = rider_mass + bike_mass


      
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
            force[n+1] = Force(speed[n+1],n)
        else:
            speed[n+1] = t_speed[n+1]
            force[n+1] = c_force[n+1]
        
        force[n+1] = np.max([0,force[n+1]])
        power[n+1] = (force[n+1] * speed[n+1])
        total_power[n+1] = Efficiency(n) + power[n+1]
        energy[n+1] = energy[n] + total_power[n+1]*(step/(60*60))
        
    return steps
   #plot each loop here


   
#simulate and plot

n = 0
#for c  in condition:
end = loop(n)
n+=1

print 'max mph = ' + repr(np.max(speed[:end])*2.23)
print 'average mph = ' + repr(np.mean(speed[:end])*2.23)
print 'average power = ' + repr(np.mean(power[:end]))
print 'max power = ' + repr(np.max(power[:end]))
print 'energy = ' + repr(np.max(energy))

#finish plot

    