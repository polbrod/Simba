# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 22:43:03 2013

@author: Nathan
"""

from scipy import optimize as opt
from scipy.interpolate import UnivariateSpline,interp1d,griddata
import math 
import numpy as np
import itertools
import collections
import logging
import wx
from os import linesep

def dependencies_for_simulation(): #missing imports needs to convert to .exe
    from scipy.sparse.csgraph import _validation


def Simulation(dict_in):

    logging.info("STARTING Simulation.py")
    for file in dict_in:
        
        currentData = dict_in[file]
    
        for key in currentData:
            if np.size(currentData[key]) > 1:
                logging.critical("Parameter %s in %s has more than 1 value",key,file)
                GUIdialog = wx.MessageDialog(None, "Parameter " + key +" in " + file + " has more than 1 value", "Error", wx.OK)
                GUIdialog.ShowModal()
                GUIdialog.Destroy()
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
        
        assert "chain_efficiency" in currentData, logging.critical("%s is missing data: chain_efficiency" % file)
        logging.info("chain_efficiency found")
        chain_efficiency = currentData["chain_efficiency"]
        
        assert "battery_efficiency" in currentData, logging.critical("%s is missing data: chain_efficiency" % file)
        logging.info("battery_efficiency found")
        battery_efficiency = currentData["battery_efficiency"]
        
        assert "motor_torque_constant" in currentData, logging.critical("%s is missing data: motor_torque_constant" % file)
        logging.info("motor_torque_constant found")
        motor_torque_constant = currentData["motor_torque_constant"] #torque to current constant of motor. torque/amp
    
        assert "motor_rpm_constant" in currentData, logging.critical("%s is missing data: motor_rpm_constant" % file)
        logging.info("motor_rpm_constant found")
        motor_rpm_constant = currentData["motor_rpm_constant"] #rpm to voltage dc constant of motor. rpm/volt

        assert "top_power" in currentData, logging.critical("%s is missing data: top_power" % file)
        logging.info("top_power found")
        top_power = currentData["top_power"]
        
        assert "dist_to_speed_lookup" in currentData, logging.critical("%s is missing data: dist_to_speed_lookup" % file)
        logging.info("dist_to_speed_lookup found")
        dist_to_speed_lookup = currentData["dist_to_speed_lookup"][0]
        
        assert "dist_to_alt_lookup" in currentData, logging.critical("%s is missing data: dist_to_alt_lookup" % file)
        logging.info("dist_to_alt_lookup found")
        dist_to_alt_lookup = currentData["dist_to_alt_lookup"][0]
        
        assert "motor_controller_eff_lookup" in currentData, logging.critical("%s is missing data: motor_controller_eff_lookup" % file)
        logging.info("motor_controller_eff_lookup found")
        motor_controller_eff_lookup = currentData["motor_controller_eff_lookup"][0]
        
        assert "motor_eff_lookup" in currentData, logging.critical("%s is missing data: motor_eff_lookup" % file)
        logging.info("motor_eff_lookup found")
        motor_eff_lookup = currentData["motor_eff_lookup"][0]


        max_distance_travel = 60600        
        
        #calc values
        top_speed = ((wheel_radius*2*np.pi* (top_rpm) / (gearing))/60)
        top_force = (top_torque * gearing) / wheel_radius
        drag_area = frontal_area * air_resistance
        mass = rider_mass + bike_mass
        steps = int(math.ceil(total_time/step))
        sqrt2 = np.sqrt(2)     
        
        #Arrays (output)
        time = np.zeros((steps+1,tests),dtype=float)
        distance = np.zeros((steps+1,tests),dtype=float)
        l_speed = np.zeros((steps+1,tests),dtype=float) #look up speed
        t_speed = np.zeros((steps+1,tests),dtype=float) #speed after compare to top
        c_force = np.zeros((steps+1,tests),dtype=float) #force before compare
        p_force = np.zeros((steps+1,tests),dtype=float) #force before power compare	  p_speed = np.zeros((steps+1,tests),dtype=float) #speed before power compare
        p_speed = np.zeros((steps+1,tests),dtype=float) #speed before power compare        
        speed = np.zeros((steps+1,tests),dtype=float)   #speed after compare (actual)
        force = np.zeros((steps+1,tests),dtype=float)   #force after compare (actual)
        c_power = np.zeros((steps+1,tests),dtype=float) #power before compare
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
        dist_to_speed_lookup = "Lookup Files\\" + dist_to_speed_lookup
        try:
            n = np.loadtxt(dist_to_speed_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
            logging.info("%s loaded", dist_to_speed_lookup)
        except IOError:
            logging.critical("Unable to load %s", dist_to_speed_lookup)
            raise Exception("Unable to load \'" + dist_to_speed_lookup + "\'")
        x = n[:,0].astype(np.float)
        y = n[:,1].astype(np.float)
	  #x = np.array([0,3220])
	  #y = np.array([1000,1000])
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
	  #x = np.array([0,3220])
	  #y = np.array([0,0])
        distancetoaltitude_lookup = interp1d(x,y)
        
        motor_controller_eff_lookup = "Lookup Files\\" + motor_controller_eff_lookup
        try:
            n = np.loadtxt(motor_controller_eff_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
            logging.info("%s loaded", motor_controller_eff_lookup)
        except IOError:
            logging.critical("Unable to load %s", motor_controller_eff_lookup)
            raise Exception("Unable to load \'" + motor_controller_eff_lookup + "\'")
        x = n[:,0].astype(np.float)
        y = n[:,1].astype(np.float)
        z = n[:,2].astype(np.float)
        points = np.transpose(np.array([x,y]))
        values = np.array(z)
        grid_x, grid_y = np.mgrid[np.min(x):np.max(x)+1, np.min(y):np.max(y)+1]
        motor_controller_eff_grid = griddata(points, values, (grid_x, grid_y), method='linear')
        #[volts_rms][amps_rms]
        
        motor_eff_lookup = "Lookup Files\\" + motor_eff_lookup
        try:
            n = np.loadtxt(motor_eff_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
            logging.info("%s loaded", motor_eff_lookup)
        except IOError:
            logging.critical("Unable to load %s", motor_eff_lookup)
            raise Exception("Unable to load \'" + motor_eff_lookup + "\'")
        x = n[:,0].astype(np.float)
        y = n[:,1].astype(np.float)
        z = n[:,2].astype(np.float)
        points = np.transpose(np.array([x,y]))
        values = np.array(z)
        grid_x, grid_y = np.mgrid[np.min(x):np.max(x)+1, np.min(y):np.max(y)+1]
        motor_eff_grid = griddata(points, values, (grid_x, grid_y), method='linear')
        #[rpm][torque]

	  #look up tests

        message = '';        
        
        if np.max(distancetospeed_lookup.x) < max_distance_travel:
            max_distance_travel =  np.max(distancetospeed_lookup.x)  
            message += 'max_distance_travel greater than speed to distance look up --- '
            message += 'max_distance_travel changed to ' + repr(max_distance_travel) + linesep
            message += linesep

        if np.max(distancetoaltitude_lookup.x) < max_distance_travel:
            max_distance_travel =  np.max(distancetoaltitude_lookup.x)  
            message += 'max_distance_travel greater than altitude to distance look up --- '
            message += 'max_distance_travel changed to ' + repr(max_distance_travel) + linesep
            message += linesep

        (x,y) = motor_eff_grid.shape
        if y-1 <  top_torque:
            top_torque = y-1
            message += 'top_torque greater than motor efficiency look up --- '
            message += 'top_torque changed to ' + repr(top_torque) + linesep
            message += linesep

        if x-1 <  top_rpm:
            top_rpm = x-1
            message += 'top_rpm greater than motor efficiency look up --- '
            message += 'top_rpm changed to ' + repr(top_rpm) + linesep
            message += linesep

        (x,y) = motor_controller_eff_grid.shape
        if y-1 <  top_torque/motor_torque_constant:
            top_torque = (y-1) * motor_torque_constant
            message += 'possible arms (from top_torque and motor torque constant) is greater than motor controller efficiency look up --- '
            message += 'top_torque changed to ' + repr(top_torque) + linesep
            message += linesep

        if x-1 <  (top_rpm/(motor_rpm_constant)*(1/(sqrt2))) :
            top_rpm = (x-1)*(motor_rpm_constant)*(1/(sqrt2)) 
            message += 'possible Vrms (from top_rpm and motor rpm constant) is greater than motor controller efficiency look up --- '
            message += 'top_rpm changed to ' + repr(top_rpm) + linesep
            
        if len(message) > 1:
            GUIdialog = wx.MessageDialog(None, message, "Warning", wx.OK)
            GUIdialog.ShowModal()
            GUIdialog.Destroy()     
         
        
        #functions

        def Power(s,n):
            return Force(s,n) * s

        def power_solve(s,n):
            return Power(s,n) - top_power
    
        def force_solve(s,n):
            return Force(s,n) - top_force
        
        def Force(s,n):
            acceleration[n+1] = mass*((s - speed[n])/step)
            drag[n+1] = 0.5 * drag_area*air_density*s**2
            altitude[n+1] = distancetoaltitude_lookup(distance[n+1])
            slope[n+1] = (altitude[n+1] - altitude[n])/(distance[n+1] - distance[n])    
            incline[n+1] = mass*gravity*slope[n+1]
            rolling[n+1] = mass*gravity*rolling_resistance
    	    return np.max([0,(acceleration[n+1] + drag[n+1] + incline[n+1] + rolling[n+1])])
        
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
                    p_speed[n+1] = (opt.fsolve(force_solve,t_speed[n+1],n))[0]
                    p_force[n+1] = Force(p_speed[n+1],n)
                else:
            	   p_speed[n+1] = t_speed[n+1]
            	   p_force[n+1] = c_force[n+1]
        
                c_power[n+1] = Power(p_speed[n+1],n)
        
                if c_power[n+1] > top_power:
                    speed[n+1] = (opt.fsolve(power_solve,p_speed[n+1],n))[0]
                    force[n+1] = Force(speed[n+1],n)
                    power[n+1] = Power(speed[n+1],n)
                else:
            	   speed[n+1] = p_speed[n+1]
            	   force[n+1] = p_force[n+1]
            	   power[n+1] = c_power[n+1]
            
                    
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
        
        newData = collections.OrderedDict()
        
        newData["Time (Seconds)"] = (time[:end])
        newData["Distance (Meters)"] = (distance[:end])
        newData["L_Speed (M/S)"] = (l_speed[:end])
        newData["T_Speed (M/S)"] = (t_speed[:end])
        newData["C_Force (N)"] = (c_force[:end])
        newData["P_Force (N)"] = (p_force[:end])
        newData["P_Speed (M/S)"] = (p_speed[:end])
        newData["Actual Speed (M/S)"] = (speed[:end])
        newData["Actual Force (N)"] = (force[:end])
        newData["C_Power [Watts]"] = (c_power[:end])
        newData["Power (Watts)"] = (power[:end])
        newData["Energy (Wh)"] = (energy[:end])
        newData["Acceleration (N)"] = (acceleration[:end])
        newData["Drag (N)"] = (drag[:end])
        newData["Altitude (Meters)"] = (altitude[:end])
        newData["Slope (Ratio)"] = (slope[:end])
        newData["Incline (N)"] = (incline[:end])
        newData["Rolling (N)"] = (rolling[:end])
        newData["Motor RPM"] = (motor_rpm[:end])
        newData["Motor Torque (Nm)"] = (motor_torque[:end])      
        newData["Motor Loss (Watts)"] = (motor_loss[:end])
        newData["Motor Controller Loss (Watts)"] = (motor_controller_loss[:end])
        newData["Chain Loss (Watts)"] = (chain_loss[:end])
        newData["Battery Loss (Watts)"] = (battery_loss[:end])
        newData["Total Power (Watts)"] = (total_power[:end])
        newData["Arms"] = (arms[:end])
        newData["Vrms"] = (vrms[:end])     
        
        newData["Average MPH"] = repr(round(np.mean(speed[:end])*2.23,3))
        newData["Max MPH"] = repr(round(np.max(speed[:end])*2.23,3))
        newData["Average Power (Watts)"] = repr(round(np.mean(power[:end]),3))
        newData["Max Power (Watts)"] = repr(round(np.max(power),3))
        newData["Max Energy (Wh)"] = repr(round(np.max(energy),3))


        dict_in[file] = newData
        logging.info("Converted %s to a dictionary successfully", file)
        
    logging.info("ENDING Simulation.py")
    return dict_in

    
