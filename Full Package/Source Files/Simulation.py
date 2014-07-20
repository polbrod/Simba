#Import important libraries 
from scipy import optimize as opt
from scipy.interpolate import griddata,interp1d
import math 
import numpy as np
import itertools
import collections
import logging
import wx
from os import linesep

from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub
from datetime import datetime

def dependencies_for_simulation(): #missing imports needs to convert to .exe
    from scipy.sparse.csgraph import _validation



def Simulation(dict_in):

    #limit variables NOT PARAMETERS
    is_batt_power = False
    is_motor_power = False

    logging.info("STARTING Simulation.py")
    for file in dict_in:
        
        currentData = dict_in[file]
    
        for key in currentData:
            if np.size(currentData[key]) > 1:
                logging.critical("Parameter %s in %s has more than 1 value",key,file)
                msg = datetime.now().strftime('%H:%M:%S') + ": " + "Parameter " + key + " in " + file + " has more than 1 value! Each parameter may only have 1 value"
                wx.CallAfter(pub.sendMessage, "AddStatus", msg)
                raise Exception("One or more params in " + file + " have two or more values. Each param can only have one value")
        
        wx.CallAfter(pub.sendMessage, "update", "")
        tests = 1
        #parameters
        logging.info("Checking to make sure file %s has needed parameters...", file)
        
        assert "step" in currentData, logging.critical("%s is missing data: step" % file)
        logging.info("Step found")
        step = currentData["step"]           #time step in seconds
        step = step + 0.0
        
        assert "total_time" in currentData, logging.critical("%s is missing data: total_time" % file)
        logging.info("total_time found")
        total_time = currentData["total_time"]
        
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
        
        assert "frontal_area" in currentData, logging.critical("%s is missing data: frontal_area" % file)
        logging.info("frontal_area found")
        frontal_area =  currentData["frontal_area"] #m^2
        
        assert "rolling_resistance" in currentData, logging.critical("%s is missing data: rolling_resistance" % file)
        logging.info("rolling_resistance found")
        rolling_resistance = currentData["rolling_resistance"]

        assert "top_motor_current" in currentData, logging.critical("%s is missing data: top_motor_current" % file)
        logging.info("top_motor_current found")
        top_motor_current = currentData['top_motor_current'] #amps        
        
        assert "top_rpm" in currentData, logging.critical("%s is missing data: top_rpm" % file)
        logging.info("top_rpm found")
        top_rpm = currentData["top_rpm"]    
            
        assert "motor_top_power" in currentData, logging.critical("%s is missing data: motor_top_power" % file)
        logging.info("motor_top_power found")
        motor_top_power = currentData["motor_top_power"]
        
        assert "battery_efficiency" in currentData, logging.critical("%s is missing data: battery_efficiency" % file)
        logging.info("battery_efficiency found")
        battery_efficiency = currentData["battery_efficiency"]
        
        assert "motor_torque_constant" in currentData, logging.critical("%s is missing data: motor_torque_constant" % file)
        logging.info("motor_torque_constant found")
        motor_torque_constant = currentData["motor_torque_constant"] #torque to current constant of motor. torque/amp
        
        assert "motor_rpm_constant" in currentData, logging.critical("%s is missing data: motor_rpm_constant" % file)
        logging.info("motor_rpm_constant found")
        motor_rpm_constant = currentData["motor_rpm_constant"] #rpm to voltage dc constant of motor. rpm/volt      
        
        assert "motor_thermal_conductivity" in currentData, logging.critical("%s is missing data: motor_thermal_conductivity" % file)
        logging.info("motor_thermal_conductivity")
        motor_thermal_conductivity = currentData["motor_thermal_conductivity"]
        
        assert "motor_heat_capacity" in currentData, logging.critical("%s is missing data: motor_heat_capacity" % file)
        logging.info("motor_heat_capacity")
        motor_heat_capacity = currentData["motor_heat_capacity"]
        
        assert "coolant_temp" in currentData, logging.critical("%s is missing data: coolant_temp" % file)
        logging.info("coolant_temp")
        coolant_temp = currentData["coolant_temp"]
        
        assert "max_motor_temp" in currentData, logging.critical("%s is missing data: max_motor_temp" % file)
        logging.info("max_motor_temp")
        max_motor_temp = currentData["max_motor_temp"]
    
        assert "series_cells" in currentData, logging.critical("%s is missing data: series_cells" % file)
        logging.info("series_cells found")
        series_cells = currentData["series_cells"]
        
        assert "max_amphour" in currentData, logging.critical("%s is missing data: max_amphour" % file)
        logging.info("max_amphour")
        max_amphour = currentData["max_amphour"]
        
        assert "batt_max_current" in currentData, logging.critical("%s is missing data: batt_max_current" % file)
        logging.info("batt_max_current")
        batt_max_current = currentData["batt_max_current"]
        
        assert "max_distance_travel" in currentData, logging.critical("%s is missing data: max_distance_travel" % file)
        logging.info("max_distance_travel found")
        max_distance_travel = currentData["max_distance_travel"]  
        
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
        
        assert "soc_to_voltage_lookup" in currentData, logging.critical("%s is missing data: soc_to_voltage_lookup" % file)
        logging.info("soc_to_voltage_lookup found")
        soc_to_voltage_lookup = currentData["soc_to_voltage_lookup"][0]
        
        assert "throttlemap_lookup" in currentData, logging.critical("%s is missing data: throttlemap_lookup" % file)
        logging.info("throttlemap_lookup found")
        throttlemap_lookup = currentData["throttlemap_lookup"][0]
   
        assert "lean_angle_lookup" in currentData, logging.critical("%s is missing data: lean_angle_lookup" % file)
        logging.info("lean_angle_lookup found")
        lean_angle_lookup = currentData["lean_angle_lookup"][0]
        
        assert "chain_efficiency_lookup" in currentData, logging.critical("%s is missing data: chain_efficiency_lookup" % file)
        logging.info("chain_efficiency_lookup found")
        chain_efficiency_lookup = currentData["chain_efficiency_lookup"][0]

        assert "corner_radius_lookup" in currentData, logging.critical("%s is missing data: corner_radius_lookup" % file)
        logging.info("corner_radius_lookup found")
        corner_radius_lookup = currentData["corner_radius_lookup"][0]
 
        assert "tyreA" in currentData, logging.critical("%s is missing data: tyreA" % file)
        logging.info("tyreA found")
        tyreA = currentData["tyreA"][0]
        #tyreA = -2.069641313760728140e-05
	
        assert "tyreB" in currentData, logging.critical("%s is missing data: tyreB" % file)
        logging.info("tyreB found")
        tyreB = currentData["tyreB"][0]
        #tyreB = 6.386679031823000125e-06
	
        assert "tyreC" in currentData, logging.critical("%s is missing data: tyreC" % file)
        logging.info("tyreC found")
        TyreC = currentData["tyreC"][0]
        #TyreC = 3.197376543933548310e-01
        
        assert "top_lean_angle" in currentData, logging.critical("%s is missing data: top_lean_angle" % file)
        logging.info("top_lean_angle found")
        top_lean_angle = currentData["top_lean_angle"][0]
        
        #top_lean_angle = 45
        
        #calc values
        
        #simulation calcs
        steps = int(math.ceil(total_time/step))
        sqrt2 = np.sqrt(2)     
        #motor_top_speed = ((wheel_radius*2*np.pi* (top_rpm) / (gearing))/60)
        #motor_top_force = (top_torque * gearing) / wheel_radius
        drag_area = frontal_area * air_resistance
        mass = rider_mass + bike_mass
        top_torque = top_motor_current * motor_torque_constant

        #Arrays (output)
        time = np.zeros((steps+1,tests),dtype=float)
        distance = np.zeros((steps+1,tests),dtype=float)
        l_speed = np.zeros((steps+1,tests),dtype=float) #look up speed
        t_speed = np.zeros((steps+1,tests),dtype=float) #speed after compare to top
        c_force = np.zeros((steps+1,tests),dtype=float) #force before compare
        p_force = np.zeros((steps+1,tests),dtype=float) #force before power compare        
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
        air_density = np.zeros((steps+1,tests),dtype=float)

        motor_rpm = np.zeros((steps+1,tests),dtype=float)
        motor_torque = np.zeros((steps+1,tests),dtype=float)
        motor_loss = np.zeros((steps+1,tests),dtype=float)
        motor_controller_loss = np.zeros((steps+1,tests),dtype=float)
        chain_loss = np.zeros((steps+1,tests),dtype=float)
        battery_loss = np.zeros((steps+1,tests),dtype=float)
        total_power = np.zeros((steps+1,tests),dtype=float) #power with losses
        arms = np.zeros((steps+1,tests),dtype=float)    #amps rms out from motor controller
        vrms = np.zeros((steps+1,tests),dtype=float)    #voltage rms out from motor controller
        
        motor_efficiency = np.zeros((steps+1,tests),dtype=float)
        motor_controller_efficiency = np.zeros((steps+1,tests),dtype=float)
        chain_power = np.zeros((steps+1,tests),dtype=float)
        motor_power = np.zeros((steps+1,tests),dtype=float)
        motor_controller_power = np.zeros((steps+1,tests),dtype=float)
        battery_power = np.zeros((steps+1,tests),dtype=float)
        
        voltage = np.zeros((steps+1,tests),dtype=float)
        top_force = np.zeros((steps+1,tests),dtype=float)
        top_speed = np.zeros((steps+1,tests),dtype=float)
        top_power = np.zeros((steps+1,tests),dtype=float)
        amphour = np.zeros((steps+1,tests),dtype=float)

        batt_power_limit = np.zeros((steps+1,tests),dtype=float)
        motor_power_limit = np.zeros((steps+1,tests),dtype=float)
        motor_torque_limit = np.zeros((steps+1,tests),dtype=float)
        motor_rpm_limit = np.zeros((steps+1,tests),dtype=float)
        
        motor_energy_in = np.zeros((steps+1,tests),dtype=float)
        motor_energy_out = np.zeros((steps+1,tests),dtype=float)
        motor_energy = np.zeros((steps+1,tests),dtype=float)
        motor_temp = np.zeros((steps+1,tests),dtype=float)
        mt_speed = np.zeros((steps+1,tests),dtype=float)
        mt_force = np.zeros((steps+1,tests),dtype=float)
        mt_power = np.zeros((steps+1,tests),dtype=float)
        mt_total_power = np.zeros((steps+1,tests),dtype=float)
        motor_thermal_limit = np.zeros((steps+1,tests),dtype=float)
        motor_thermal_error = np.zeros((steps+1,tests),dtype=float)
        
        wheel_radius = np.zeros((steps+1,tests),dtype=float)
        lean_angle_limit = np.zeros((steps+1,tests),dtype=float)
        lateral_acc = np.zeros((steps+1, tests), dtype=float)        
        
        #Lookups
        dist_to_speed_lookup = "Lookup Files\\" + dist_to_speed_lookup
        try:
            n = np.loadtxt(dist_to_speed_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
            '''
            logging.info("%s loaded", dist_to_speed_lookup)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + dist_to_speed_lookup + " loaded"
            pub.sendMessage(("AddStatus"), msg)             
            '''
        except IOError:
            logging.critical("Unable to load %s", dist_to_speed_lookup)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Unable to load " + dist_to_speed_lookup + " from " + file+ ". Make sure the file exists and is not open."
            wx.CallAfter(pub.sendMessage, "AddStatus", msg)
            raise Exception("Unable to load \'" + dist_to_speed_lookup + "\'")

        x = n[:,0].astype(np.float)
        y = n[:,1].astype(np.float)
        #x = np.array([0,3220])
	   #y = np.array([1000,1000])
        distancetospeed_lookup = interp1d(x,y)
          

            
        #Lookups
        soc_to_voltage_lookup = "Lookup Files\\" + soc_to_voltage_lookup
        try:
            n = np.loadtxt(soc_to_voltage_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
            logging.info("%s loaded", soc_to_voltage_lookup)

        except IOError:
            logging.critical("Unable to load %s", soc_to_voltage_lookup)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Unable to load " + soc_to_voltage_lookup + " from " + file + ". Make sure the file exists and is not open."
            wx.CallAfter(pub.sendMessage, "AddStatus", msg)
            raise Exception("Unable to load \'" + soc_to_voltage_lookup + "\'")
            
        x = n[:,0].astype(np.float)
        y = n[:,1].astype(np.float)

        soctovoltage_lookup = interp1d(x,y)
       

        
        dist_to_alt_lookup = "Lookup Files\\" + dist_to_alt_lookup
        try:
            n = np.loadtxt(dist_to_alt_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
            logging.info("%s loaded", dist_to_alt_lookup)
            
        except IOError:
            logging.critical("Unable to load %s", dist_to_alt_lookup)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Unable to load " + dist_to_alt_lookup + " from " + file + ". Make sure the file exists and is not open."
            wx.CallAfter(pub.sendMessage, "AddStatus", msg)
            raise Exception("Unable to load \'" + dist_to_alt_lookup + "\'")
        x = n[:,0].astype(np.float)
        y = n[:,1].astype(np.float)

        distancetoaltitude_lookup = interp1d(x,y)
        
        
        throttlemap_lookup = "Lookup Files\\" + throttlemap_lookup
        try:
            n = np.loadtxt(throttlemap_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
            logging.info("%s loaded", throttlemap_lookup)
            
        except IOError:
            logging.critical("Unable to load %s", throttlemap_lookup)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Unable to load " + throttlemap_lookup + " from " + file + ". Make sure the file exists and is not open."
            wx.CallAfter(pub.sendMessage, "AddStatus", msg)
            raise Exception("Unable to load \'" + throttlemap_lookup + "\'")
        x = n[:,0].astype(np.float)
        y = n[:,1].astype(np.float)
        throttlemap = interp1d(x,y)        
        
        #distance_to_lean_angle_lookup
        lean_angle_lookup = "Lookup Files\\" + lean_angle_lookup
        try:
            n = np.loadtxt(lean_angle_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
            logging.info("%s loaded", lean_angle_lookup)
    
        except IOError:
            logging.critical("Unable to load %s", lean_angle_lookup)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Unable to load " + lean_angle_lookup + " from " + file + ". Make sure the file exists and is not open."
            wx.CallAfter(pub.sendMessage, "AddStatus", msg)
            raise Exception("Unable to load \'" + lean_angle_lookup + "\'")
        x = n[:,0].astype(np.float)
        y = n[:,1].astype(np.float)
        lean_angle_lookup = interp1d(x,y)
   
        motor_controller_eff_lookup = "Lookup Files\\" + motor_controller_eff_lookup
        try:
            n = np.loadtxt(motor_controller_eff_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
            logging.info("%s loaded", motor_controller_eff_lookup)
            
        except IOError:
            logging.critical("Unable to load %s", motor_controller_eff_lookup)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Unable to load " + motor_controller_eff_lookup + " from " + file + ". Make sure the file exists and is not open."
            wx.CallAfter(pub.sendMessage, "AddStatus", msg)
            raise Exception("Unable to load \'" + motor_controller_eff_lookup + "\'")
            
        x = n[:,0].astype(np.float)
        y = n[:,1].astype(np.float)
        z = n[:,2].astype(np.float)
        points = np.transpose(np.array([x,y]))
        values = np.array(z)
        grid_x, grid_y = np.mgrid[np.min(x):np.max(x)+1, np.min(y):np.max(y)+1]
        motor_controller_eff_grid = griddata(points, values, (grid_x, grid_y), method='linear')

        
        motor_eff_lookup = "Lookup Files\\" + motor_eff_lookup
        try:
            n = np.loadtxt(motor_eff_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
            logging.info("%s loaded", motor_eff_lookup)
            
        except IOError:
            logging.critical("Unable to load %s", motor_eff_lookup)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Unable to load " + motor_eff_lookup + " from " + file + ". Make sure the file exists and is not open."
            wx.CallAfter(pub.sendMessage, "AddStatus", msg) 
            raise Exception("Unable to load \'" + motor_eff_lookup + "\'")

        x = n[:,0].astype(np.float)
        y = n[:,1].astype(np.float)
        z = n[:,2].astype(np.float)
        points = np.transpose(np.array([x,y]))
        values = np.array(z)
        grid_x, grid_y = np.mgrid[np.min(x):np.max(x)+1, np.min(y):np.max(y)+1]
        motor_eff_grid = griddata(points, values, (grid_x, grid_y), method='linear')


        #chain efficiency
        #rpm to chain efficiency %
        chain_efficiency_lookup = "Lookup Files\\" + chain_efficiency_lookup
        try:
            n = np.loadtxt(chain_efficiency_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
            logging.info("%s loaded", chain_efficiency_lookup)
            
        except IOError:
            logging.critical("Unable to load %s", chain_efficiency_lookup)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Unable to load " + chain_efficiency_lookup + " from " + file + ". Make sure the file exists and is not open."
            wx.CallAfter(pub.sendMessage, "AddStatus", msg)
            raise Exception("Unable to load \'" + chain_efficiency_lookup + "\'")
        n = np.loadtxt(chain_efficiency_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
        x = n[:,0].astype(np.float)
        y = n[:,1].astype(np.float)
        chain_efficiency_map = interp1d(x,y)

        #distance to corner radius lookup
        corner_radius_lookup = "Lookup Files\\" + corner_radius_lookup
        try:
            n = np.loadtxt(corner_radius_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
            logging.info("%s loaded", corner_radius_lookup)
            
        except IOError:
            logging.critical("Unable to load %s", corner_radius_lookup)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Unable to load " + corner_radius_lookup + " from " + file + ". Make sure the file exists and is not open."
            wx.CallAfter(pub.sendMessage, "AddStatus", msg)
            raise Exception("Unable to load \'" + corner_radius_lookup + "\'")
        n = np.loadtxt(corner_radius_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
        x = n[:,0].astype(np.float)
        y = n[:,1].astype(np.float)
        cornerradius = interp1d(x,y)

        message = '';        
        
        #Make sure parameters don't extend lookups
        if np.max(distancetospeed_lookup.x) < max_distance_travel:
            max_distance_travel =  np.max(distancetospeed_lookup.x)  
            message = datetime.now().strftime('%H:%M:%S') + ": "
            message += 'WARNING: max_distance_travel greater than speed to distance look up --- '
            message += 'max_distance_travel changed to ' + repr(max_distance_travel) + " for file " + file
            wx.CallAfter(pub.sendMessage, "AddStatus", message) 

        if np.max(distancetoaltitude_lookup.x) < max_distance_travel:
            max_distance_travel =  np.max(distancetoaltitude_lookup.x)  
            message = datetime.now().strftime('%H:%M:%S') + ": "
            message += 'WARNING: max_distance_travel greater than altitude to distance look up --- '
            message += 'max_distance_travel changed to ' + repr(max_distance_travel) + " for file " + file
            wx.CallAfter(pub.sendMessage, "AddStatus", message)
            
        if np.max(throttlemap.x) < top_rpm:
            top_rpm = np.max(throttlemap.x)
            message = datetime.now().strftime('%H:%M:%S') + ": "
            message += 'WARNING: top rpm is greater than throttle map look up --- '
            message += 'top rpm changed to ' + repr(top_rpm) + " for file " + file
            wx.CallAfter(pub.sendMessage, "AddStatus", message)
            
        (x,y) = motor_eff_grid.shape
        if y-1 <  top_torque:
            top_torque = y-1
            top_motor_current = (y-1)/motor_torque_constant
            message = datetime.now().strftime('%H:%M:%S') + ": "
            message += 'WARNING: top_torque greater than motor efficiency look up --- '
            message += 'top_torque changed to ' + repr(top_torque) + ', top_motor_current changed to ' + repr(top_motor_current)
            message += " for file " + file
            wx.CallAfter(pub.sendMessage, "AddStatus", message)
            
        if x-1 <  top_rpm:
            top_rpm = x-1
            message = datetime.now().strftime('%H:%M:%S') + ": "
            message += 'WARNING: top_rpm greater than motor efficiency look up --- '
            message += 'top_rpm changed to ' + repr(top_rpm) + " for file " + file
            wx.CallAfter(pub.sendMessage, "AddStatus", message)

        (x,y) = motor_controller_eff_grid.shape
        if y-1 <  top_torque/motor_torque_constant:
            top_torque = (y-1) * motor_torque_constant
            top_motor_current = y-1
            message = datetime.now().strftime('%H:%M:%S') + ": "
            message += 'WARNING: possible arms (from top_torque and motor torque constant) is greater than motor controller efficiency look up --- '
            message += 'top_torque changed to ' + repr(top_torque) + ' for file ' + file
            message = datetime.now().strftime('%H:%M:%S') + ": "
            message += 'WARNING: possible arms (from top_motor_current and motor torque constant) is greater than motor controller efficiency look up --- '
            message += 'top_motor_current changed to ' + repr(top_motor_current) + ' for file ' + file
            wx.CallAfter(pub.sendMessage, "AddStatus", message)
    
        if x-1 <  (top_rpm/(motor_rpm_constant)*(1/(sqrt2))) :
            top_rpm = (x-1)*(motor_rpm_constant)*(1/(sqrt2)) 
            message = datetime.now().strftime('%H:%M:%S') + ": "
            message += 'WARNING: possible Vrms (from top_rpm and motor rpm constant) is greater than motor controller efficiency look up --- '
            message += 'top_rpm changed to ' + repr(top_rpm) + ' for file ' + file
            wx.CallAfter(pub.sendMessage, "AddStatus", message)
            
        if np.max(lean_angle_lookup.x) < max_distance_travel:
            max_distance_travel =  np.max(lean_angle_lookup.x)  
            message = datetime.now().strftime('%H:%M:%S') + ": "
            message += 'WARNING: max_distance_travel greater than lean angle to distance look up --- '
            message += 'max_distance_travel changed to ' + repr(max_distance_travel) + ' for file ' + file
            wx.CallAfter(pub.sendMessage, "AddStatus", message)
            
        if np.max(chain_efficiency_map.x) < top_rpm:
            top_rpm = np.max(chain_efficiency_map.x)
            message = datetime.now().strftime('%H:%M:%S') + ": "
            message += 'WARNING: top rpm is greater than the chain efficiency look up --- '
            message += 'top rpm changed to ' + repr(top_rpm) + ' for file ' + file
            wx.CallAfter(pub.sendMessage, "AddStatus", message)
        
        if np.max(cornerradius.x) < max_distance_travel:
            max_distance_travel = np.max(cornerradius.x)
            message = datetime.now().strftime('%H:%M:%S') + ": "
            message += 'WARNING: max_distance_travel is greater than cornerradius to distance look up --- '
            message += 'max_distance_travel changed to ' + repr(max_distance_travel) + ' for file ' + file
            wx.CallAfter(pub.sendMessage, "AddStatus", message)
            
        wx.CallAfter(pub.sendMessage, "update", "")   
        '''
        if len(message) > 1:
            GUIdialog = wx.MessageDialog(None, message, "Warning", wx.OK)
            GUIdialog.ShowModal()
            GUIdialog.Destroy()     
        '''
        
        #functions
        #Find power at point n+1
        def Power(s,n):
            return Force(s,n) * s

        #Solve for when power_solve = 0
        #Finds max speed given max power
        def power_solve(s,n):
            return Power(s,n) - top_power[n+1]
    
        #Solve for when force_solve = 0
        #Finds max speed given max power    
        def force_solve(s,n):
            return Force(s,n) - top_force[n+1]
        
        #Find Force at point n+1
        def Force(s,n):
            acceleration[n+1] = mass*((s - speed[n])/step)
            altitude[n+1] = distancetoaltitude_lookup(distance[n+1])
            air_density[n+1] = (((altitude[n+1]/1000)-44.3308)/-42.2665) ** 4.25588
            drag[n+1] = 0.5 * drag_area*air_density[n+1]*s**2
            slope[n+1] = (altitude[n+1] - altitude[n])/(distance[n+1] - distance[n])    
            incline[n+1] = mass*gravity*slope[n+1]
            rolling[n+1] = mass*gravity*rolling_resistance
            return np.max([0,(acceleration[n+1] + drag[n+1] + incline[n+1] + rolling[n+1])])
        
        #Find Efficiency given speed, force, power at point n+1
        def Efficiency(s,f,p,n):
            motor_rpm[n+1] = ((s)/(wheel_radius[n+1]*2*np.pi)) * gearing * 60
            motor_torque[n+1] = (f * wheel_radius[n+1])/gearing
            arms[n+1] = motor_torque[n+1]/motor_torque_constant
            vrms[n+1] = motor_rpm[n+1]/(motor_rpm_constant)*(1/(sqrt2))  
            
            motor_efficiency[n+1] = motor_eff_grid[np.int(np.around(motor_rpm[n+1]))][np.int(np.around(motor_torque[n+1]))]
            motor_controller_efficiency[n+1] = motor_controller_eff_grid[np.int(np.around(vrms[n+1]))][np.int(np.around(arms[n+1]))]
            
            chain_power[n+1] = (p/(chain_efficiency_map(motor_rpm[[n+1]])))
            motor_power[n+1] = (chain_power[n+1]/(motor_efficiency[n+1]))
            motor_controller_power[n+1] = (motor_power[n+1]/(motor_controller_efficiency[n+1]))
            battery_power[n+1] = (motor_controller_power[n+1]/(battery_efficiency))
            
            motor_loss[n+1] = motor_power[n+1]*(1-motor_efficiency[n+1])
            motor_controller_loss[n+1] = motor_controller_power[n+1]*(1-motor_controller_efficiency[n+1])
            chain_loss[n+1] = chain_power[n+1]*(1-chain_efficiency_map(motor_rpm[n+1]))
            battery_loss[n+1] = battery_power[n+1]*(1-battery_efficiency)
            return battery_power[n+1]
 
        #Battery voltage at point n
        def Battery_Voltage(n):
            return series_cells*soctovoltage_lookup(max([0,1-(amphour[n]/max_amphour)]))
             
        #Top force (allows for expandsion to more than one top forces)
        def Top_force(n):
            return ((throttlemap(motor_rpm[n]) * top_motor_current * motor_torque_constant) * gearing) / wheel_radius[n+1]
                
        #Top Speed(allows for expandsion to one top speeds)
        def Top_speed(n):
            return ((wheel_radius[n+1]*2*np.pi* (top_rpm) / (gearing))/60)
                    
        #Top Power 
        #check which has lower top power battery or motor
        def Top_power(n):
            global is_motor_power
            global is_batt_power
            batt_top_power = voltage[n+1] * batt_max_current
            if motor_top_power < batt_top_power:
                is_motor_power = True 
                is_batt_power = False
                return motor_top_power
            else:
                is_motor_power = False
                is_batt_power = True
                return batt_top_power
              
        #Find motor thermal values at point n+1
        def Motor_Thermal(n):
            motor_energy_in[n+1] = motor_loss[n] * step
            motor_energy_out[n+1] = motor_thermal_conductivity*(motor_temp[n]-coolant_temp)*step
            motor_energy[n+1] = motor_energy_in[n+1] - motor_energy_out[n+1]
            motor_temp[n+1] = motor_temp[n] + motor_energy[n+1]/motor_heat_capacity 
        
        #Solve for when Motor_Thermal_solve = 0
        #Finds max speed given other forces and thermal limits   
        #save error of solving. Thermal limits are hard to solve for
        def Motor_Thermal_solve(s,n):
            f = Force(s,n)
            p = Power(s,n)
            Efficiency(s,f,p,n)
            Motor_Thermal(n)
            motor_thermal_error[n+1] = abs(motor_temp[n+1] - max_motor_temp)
            return motor_thermal_error[n+1]   

        def Wheel_Radius(lean,n):
            if abs(lean) > top_lean_angle:
                lean = top_lean_angle
                lean_angle_limit[n+1] = 1
            return tyreA*lean**2 + tyreB*lean + TyreC

        #initial condidtions
        distance[0] = .1 #can't be 0 because not in look up
        speed[0] = .1 #can't be 0 or the bike will never start moving
        altitude[0] = distancetoaltitude_lookup(1)
        air_density[0] = (((altitude[0]/1000)-44.3308)/-42.2665) ** 4.25588
        voltage[0] = soctovoltage_lookup(0) * series_cells
        

        def loop(n):
            for n in range(steps):
                time[n+1] = time[n] + step                  #increase time step
                distance[n+1] = distance[n] + speed[n]*step #move bike forward 
                if (distance[n+1] > max_distance_travel):
                    return n                                #stop if cross finish line
                    
                wheel_radius[n+1] = Wheel_Radius(lean_angle_lookup(distance[n+1]), n)
                voltage[n+1] = Battery_Voltage(n)
                top_force[n+1] = Top_force(n)
                top_speed[n+1] = Top_speed(n)
                top_power[n+1] = Top_power(n)
                

                l_speed[n+1] = distancetospeed_lookup(distance[n+1])
                
                if l_speed[n+1] > top_speed[n+1]:           #Limit speed to top speed
                    motor_rpm_limit[n+1] = 1
                    t_speed[n+1] = top_speed[n+1]
                else:
                    t_speed[n+1] = l_speed[n+1]
                    
                
                c_force[n+1] = Force(t_speed[n+1],n)
                
                if c_force[n+1] > top_force[n+1]:           #Limit speed to top force
                    motor_torque_limit[n+1] = 1
                    p_speed[n+1] = (opt.fsolve(force_solve,t_speed[n+1],n))[0]
                    p_force[n+1] = Force(p_speed[n+1],n)
                else:
                    p_speed[n+1] = t_speed[n+1]
                    p_force[n+1] = c_force[n+1]
                
                c_power[n+1] = Power(p_speed[n+1],n)
                
                if c_power[n+1] > top_power[n+1]:           #Limit speed to top power
                    if is_motor_power:
                        motor_power_limit[n+1] = 1
                    if is_batt_power:
                        batt_power_limit[n+1] = 1
                    mt_speed[n+1] = (opt.fsolve(power_solve,p_speed[n+1],n))[0]
                    mt_force[n+1] = Force(mt_speed[n+1],n)
                    mt_power[n+1] = Power(mt_speed[n+1],n)
                else:
                    mt_speed[n+1] = p_speed[n+1]
                    mt_force[n+1] = p_force[n+1]
                    mt_power[n+1] = c_power[n+1]
                    
                mt_total_power[n+1] = Efficiency(mt_speed[n+1],mt_force[n+1],mt_power[n+1],n)
                #thermal 
                #Motor
                Motor_Thermal(n)                            #Limit speed to thermal limtis
                if motor_temp[n+1] > max_motor_temp:
                    bnds = [(0,mt_speed[n+1])]
                    speed[n+1] = (opt.fmin_tnc(Motor_Thermal_solve,mt_speed[n+1]-1,args = (n,),bounds=bnds, approx_grad = True, messages = 0))[0]
                    force[n+1] = Force(speed[n+1],n)
                    power[n+1] = Power(speed[n+1],n)   
                    total_power[n+1] = Efficiency(speed[n+1],force[n+1],power[n+1],n)
                    motor_thermal_limit[n+1] = 1 
                else:
                    speed[n+1] = mt_speed[n+1]
                    force[n+1] = mt_force[n+1]
                    power[n+1] = mt_power[n+1]   
                    total_power[n+1] = mt_total_power[n+1]
                
                #Find amphours and energy
                amphour[n+1] = amphour[n] + (total_power[n+1]/voltage[n+1])*(step/(60.0*60.0))
                energy[n+1] = energy[n] + total_power[n+1]*(step/(60.0*60.0))
                lateral_acc[n+1] = speed[n+1]**2/cornerradius(distance[n+1])
                
            return steps
           #plot each loop here
        
        
           
        #simulate and plot
        
        n = 0

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
        newData["Lateral Acceleration (N)"] = (lateral_acc[:end])
        newData["Drag (N)"] = (drag[:end])
        newData["Altitude (Meters)"] = (altitude[:end])
        newData["Slope (Ratio)"] = (slope[:end])
        newData["Incline (N)"] = (incline[:end])
        newData["Rolling (N)"] = (rolling[:end])
        newData["Air Density(kg/m^3)"] = (air_density[:end])
        newData["Motor RPM"] = (motor_rpm[:end])
        newData["Motor Torque (Nm)"] = (motor_torque[:end])      
        newData["Motor Loss (Watts)"] = (motor_loss[:end])
        newData["Motor Controller Loss (Watts)"] = (motor_controller_loss[:end])
        newData["Chain Loss (Watts)"] = (chain_loss[:end])
        newData["Battery Loss (Watts)"] = (battery_loss[:end])
        newData["Total Power (Watts)"] = (total_power[:end])
        newData["Arms"] = (arms[:end])
        newData["Vrms"] = (vrms[:end])     
        newData["Motor Energy In (J)"] = (motor_energy_in[:end])
        newData["Motor Energy Out (J)"] = (motor_energy_out[:end])
        newData["Motor Energy (J)"] = (motor_energy[:end])
        newData["Motor Temp (C)"] = (motor_temp[:end])
        newData["MT_Speed (M/S)"] = (mt_speed[:end])
        newData["MT Force (N)"] = (mt_force[:end])
        newData["MT Power (Watts)"] = (mt_power[:end])
        newData["MT Total Power (Watts)"] = (mt_total_power[:end])
        newData["Motor Efficiency"] = (motor_efficiency[:end])
        newData["Motor Controller Efficiency"] = (motor_controller_efficiency[:end])
        newData["Chain Power (watts)"] = (chain_power[:end])
        newData["Motor Power (Watts)"] = (motor_power[:end])
        newData["Motor Controller Power (Watts)"] = (motor_controller_power[:end])
        newData["Battery Power (Watts)"] = (battery_power[:end])
        newData["Voltage"] = (voltage[:end])
        newData["Top Force (N)"] = (top_force[:end])
        newData["Top Speed (M/S)"] = (top_speed[:end])
        newData["Top Power (Watts)"] = (top_power[:end])
        newData["Amphours"] = (amphour[:end])
        newData["Battery Power Limit"] = (batt_power_limit[:end])
        newData["Motor Power Limit"] = (motor_power_limit[:end])
        newData["Motor Torque Limit"] = (motor_torque_limit[:end])
        newData["Motor RPM Limit"] = (motor_rpm_limit[:end])
        newData["Motor Thermal Limit"] = (motor_thermal_limit[:end])
        newData["Motor Thermal Error"] = (motor_thermal_error[:end])
        newData["Lean Angle Limit"] = (lean_angle_limit[:end])
        newData["% Motor RPM Limit"] = (np.mean(motor_rpm_limit[:end])*100)
        newData["% Motor Torque Limit"] = (np.mean(motor_torque_limit[:end])*100)
        newData["% Motor Power Limit"] = (np.mean(motor_power_limit[:end])*100)
        newData["% Battery Power Limit"] = (np.mean(batt_power_limit[:end])*100)
        newData["% Motor Thermal Limit"] = (np.mean(motor_thermal_limit[:end])*100)
        newData["% Lean Angle Limit"] = (np.mean(lean_angle_limit[:end])*100)

        newData["Finish Time (s)"] = time[end][0]
        newData["Average MPH"] = (round(np.mean(speed[:end])*2.23,3))
        newData["Max MPH"] = (round(np.max(speed[:end])*2.23,3))
        newData["Average Power (Watts)"] = (round(np.mean(power[:end]),3))
        newData["Max Power (Watts)"] = (round(np.max(power),3))
        newData["Max Energy (Wh)"] = (round(np.max(energy),3))
        newData["Max Amphours"] = (round(np.max(amphour),3))
        newData['Max Lateral Acceleration (N)'] = np.nanmax(lateral_acc)
        
 

        dict_in[file] = newData
        logging.info("Converted %s to a dictionary successfully", file)
        wx.CallAfter(pub.sendMessage, "update", "")

        
    logging.info("ENDING Simulation.py")
    return dict_in


    
