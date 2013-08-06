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

def dependencies_for_simulation(): #missing imports needs to convert to .exe
    from scipy.sparse.csgraph import _validation

def Simulation(dict_in):

    for file in dict_in:
        
        currentData = dict_in[file]
    
        for key in currentData:
            if np.size(currentData[key]) > 1:
                raise Exception("One or more params in " + file + "have two or more values. Each param can only have one value")

        tests = 1
	#parameters
	
        assert "step" in currentData, "%r is missing data: step" % file
        step = currentData["step"]           #time step in seconds
        assert "total_time" in currentData, "%r is missing data: total_time" % file        
        total_time = currentData["total_time"]
        assert "wheel_radius" in currentData, "%r is missing data: wheel_radius" % file
        wheel_radius = currentData["wheel_radius"] #meters
        assert "gearing" in currentData, "%r is missing data: gearing" % file
        gearing = currentData["gearing"]
        assert "rider_mass" in currentData, "%r is missing data: rider_mass" % file
        rider_mass = currentData["rider_mass"] #kg
        assert "bike_mass" in currentData, "%r is missing data: bike_mass" % file
        bike_mass = currentData["bike_mass"] #kg
        assert "gravity" in currentData, "%r is missing data: gravity" % file
        gravity = currentData["gravity"] 
        assert "air_resistance" in currentData, "%r is missing data: air_resistance" % file
        air_resistance = currentData["air_resistance"]
        assert "air_density" in currentData, "%r is missing data: air_density" % file
        air_density = currentData["air_density"]
        assert "frontal_area" in currentData, "%r is missing data: frontal_area" % file
        frontal_area =  currentData["frontal_area"] #m^2
        assert "rolling_resistance" in currentData, "%r is missing data: rolling_resistance" % file
        rolling_resistance = currentData["rolling_resistance"]
        assert "top_torque" in currentData, "%r is missing data: top_torque" % file
        top_torque = currentData["top_torque"] #nm
        assert "top_rpm" in currentData, "%r is missing data: top_rpm" % file
        top_rpm = currentData["top_rpm"]
        assert "efficiency" in currentData, "%r is missing data: efficiency" % file
        efficiency = currentData["efficiency"]
        assert "max_distance_travel" in currentData, "%r is missing data: max_distance_travel" % file
        max_distance_travel = currentData["max_distance_travel"] #meters       
        assert "dist_to_speed_lookup" in currentData, "%r is missing data: dist_to_speed_lookup" % file
        dist_to_speed_lookup = currentData["dist_to_speed_lookup"][0]
        assert "dist_to_alt_lookup" in currentData, "%r is missing data: dist_to_alt_lookup" % file
        dist_to_alt_lookup = currentData["dist_to_alt_lookup"][0]

	
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
        dist_to_speed_lookup = "Lookup Files\\" + dist_to_speed_lookup
        try:
            n = np.loadtxt(dist_to_speed_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
        except IOError:
            raise Exception("Unable to load \'" + dist_to_speed_lookup + "\'")
        x = n[:,0].astype(np.float)
        y = n[:,1].astype(np.float)
        distancetospeed_lookup = interp1d(x,y)
        
        dist_to_alt_lookup = "Lookup Files\\" + dist_to_alt_lookup
        try:
            n = np.loadtxt(dist_to_alt_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
        except IOError:
            raise Exception("Unable to load \'" + dist_to_alt_lookup + "\'")
        x = n[:,0].astype(np.float)
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
                    force[n+1] = Force(speed[n+1],n)
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
        
        newData = dict()
        
        newData["Average MPH"] = repr(np.mean(speed[:end])*2.23)
        newData["Average Power (Watts)"] = repr(np.mean(power[:end])*2.23)
        newData["Max Power (Watts)"] = repr(np.max(power))
        newData["Energy (KW/Hr)"] = repr(np.max(energy))

        dict_in[file] = newData
    return dict_in

    