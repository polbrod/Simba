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
import collections
import logging

def dependencies_for_simulation(): #missing imports needs to convert to .exe
    from scipy.sparse.csgraph import _validation

def Simulation(dict_in):

    logging.info("STARTING Simulation.py")
    for file in dict_in:
        
        currentData = dict_in[file]
    
        for key in currentData:
            if np.size(currentData[key]) > 1:
                logging.critical("Parameter %s in %s has more than 1 value",key,file)
                raise Exception("One or more params in " + file + " have two or more values. Each param can only have one value")

        tests = 1
	#parameters
        logging.info("Checking to make sure file %s has needed parameters...", file)
        
        assert "step" in currentData, logging.critical("%s is missing data: step" % file)
        logging.info("Step found")
        step = currentData["step"]           #time step in seconds
        
        assert "total_time" in currentData, logging.critical("%s is missing data: total_time" % file)
        logging.info("total_time found")
        total_time = currentData["total_time"]
        
        assert "wheel_radius" in currentData, logging.critical("%s is missing data: wheel_radius" % file)
        logging.info("wheel_radius found")
        wheel_radius = currentData["wheel_radius"] #meters
        
        assert "gearing" in currentData, logging.critical("%s is missing data: gearing" % file)
        logging.info("gearing found")
        gearing = currentData["gearing"]
        
        assert "rider_mass" in currentData, logging.critical("%s is missing data: rider_mass" % file)
        logging.info("rider_mass found")
        rider_mass = currentData["rider_mass"] #kg
        
        
        assert "bike_mass" in currentData, logging.critical("%s is missing data: bike_mass" % file)
        logging.info("bike_mass found")
        bike_mass = currentData["bike_mass"] #kg
        
        assert "gravity" in currentData, logging.critical("%s is missing data: gravity" % file)
        logging.info("gravity found")
        gravity = currentData["gravity"] 
        
        assert "air_resistance" in currentData, logging.critical("%s is missing data: air_resistance" % file)
        logging.info("air_resistance found")
        air_resistance = currentData["air_resistance"]
        
        assert "air_density" in currentData, logging.critical("%s is missing data: air_density" % file)
        logging.info("air_density found")
        air_density = currentData["air_density"]
        
        assert "frontal_area" in currentData, logging.critical("%s is missing data: frontal_area" % file)
        logging.info("frontal_area found")
        frontal_area =  currentData["frontal_area"] #m^2
        
        assert "rolling_resistance" in currentData, logging.critical("%s is missing data: rolling_resistance" % file)
        logging.info("rolling_resistance found")
        rolling_resistance = currentData["rolling_resistance"]
        
        assert "top_torque" in currentData, logging.critical("%s is missing data: top_torque" % file)
        logging.info("top_torque found")
        top_torque = currentData["top_torque"] #nm
        
        assert "top_rpm" in currentData, logging.critical("%s is missing data: top_rpm" % file)
        logging.info("top_rpm found")
        top_rpm = currentData["top_rpm"]
        
        assert "efficiency" in currentData, logging.critical("%s is missing data: efficiency" % file)
        logging.info("efficiency found")
        efficiency = currentData["efficiency"]
        
        assert "max_distance_travel" in currentData, logging.critical("%s is missing data: max_distance_travel" % file)
        logging.info("max_distance_travel found")
        max_distance_travel = currentData["max_distance_travel"] #meters       
        
        assert "dist_to_speed_lookup" in currentData, logging.critical("%s is missing data: dist_to_speed_lookup" % file)
        logging.info("dist_to_speed_lookup found")
        dist_to_speed_lookup = currentData["dist_to_speed_lookup"][0]
        
        assert "dist_to_alt_lookup" in currentData, logging.critical("%s is missing data: dist_to_alt_lookup" % file)
        logging.info("dist_to_alt_lookup found")
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
            logging.info("%s loaded", dist_to_speed_lookup)
        except IOError:
            logging.critical("Unable to load %s", dist_to_speed_lookup)
            raise Exception("Unable to load \'" + dist_to_speed_lookup + "\'")
        x = n[:,0].astype(np.float)
        y = n[:,1].astype(np.float)
        distancetospeed_lookup = interp1d(x,y)
        
        dist_to_alt_lookup = "Lookup Files\\" + dist_to_alt_lookup
        try:
            n = np.loadtxt(dist_to_alt_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
            logging.info("%s loaded", dist_to_alt_lookup)
        except IOError:
            logging.critical("Unable to load %s", dist_to_alt_lookup)
            raise Exception("Unable to load \'" + dist_to_alt_lookup + "\'")
        x = n[:,0].astype(np.float)
        y = n[:,1].astype(np.float)
        distancetoaltitude_lookup = interp1d(x,y)
        
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
        
        newData = collections.OrderedDict()
        
        newData["Time (Seconds)"] = (time[:end])
        newData["Distance (Meters)"] = (distance[:end])
        newData["L_Speed (M/S)"] = (l_speed[:end])
        newData["T_Speed (M/S)"] = (t_speed[:end])
        newData["C_Force (N)"] = (c_force[:end])
        newData["Actual Speed (M/S)"] = (speed[:end])
        newData["Actual Force (N)"] = (force[:end])
        newData["Power (Watts)"] = (power[:end])
        newData["Energy (Watt/Hr)"] = (energy[:end])
        newData["Acceleration (N)"] = (acceleration[:end])
        newData["Drag (N)"] = (drag[:end])
        newData["Altitude (Meters)"] = (altitude[:end])
        newData["Slope (Ratio)"] = (slope[:end])
        newData["Incline (N)"] = (incline[:end])
        newData["Rolling (N)"] = (rolling[:end])
        newData["Average MPH"] = repr(np.mean(speed[:end])*2.23)
        newData["Average Power (Watts)"] = repr(np.mean(power[:end])*2.23)
        newData["Max Power (Watts)"] = repr(np.max(power))
        newData["Max Energy (KW/Hr)"] = repr(np.max(energy))

        dict_in[file] = newData
        logging.info("Converted %s to a dictionary successfully", file)
        
    logging.info("ENDING Simulation.py")
    return dict_in

    