
#Import important libraries 
from scipy import optimize as opt
from scipy.interpolate import griddata,interp1d
import math 
import numpy as np


#limit variables NOT PARAMETERS
is_batt_power = False
is_motor_power = False

tests = 1

#parameters
step = .5       #time step in seconds
total_time = 3600.0

#wheel_radius = 0.323596 #meters
gearing = 44/21.0

rider_mass = 97 
bike_mass = 267.6195 #kg

gravity = 9.81

air_resistance = .45
#air_density = 1.204 #now calculated based on altitude
frontal_area =  1 #m^2

rolling_resistance = 0.02973

#top_torque = 240.0 #nm no longer used calculatede below
top_rpm = 3000

motor_top_power = 80000.0
max_distance_travel = 60350.0 #meters this needs to be calculated from lookups

#chain_efficiency = .98 #no longer used with new lookup table
battery_efficiency = .98

motor_torque_constant = 2   #torque to current constant of motor. torque/amp
motor_rpm_constant = 12.0   #rpm to voltage dc constant of motor. rpm/volt

series_cells = 110.0
max_amphour = 40.0
batt_max_current = 280

motor_thermal_conductivity = 20
motor_heat_capacity = 4000.0
coolant_temp = 13.0
max_motor_temp = 115.0

#wheel_radius = tyreA*lean_angle**2 + tyreB*lean_angle + TyreC
tyreA = -2.069641313760728140e-05
tyreB = 6.386679031823000125e-06
TyreC = 3.15e-01

top_lean_angle = 38

top_motor_current = 240.0 #Amps

#lookup files
dist_to_speed_lookup = 'disttospeed.csv'
dist_to_alt_lookup = 'disttoalt.csv'
motor_controller_eff_lookup = 'Tritium_ws200_eff.csv'
motor_eff_lookup = 'Emrax_eff.csv'
soc_to_voltage_lookup = 'aee.csv'
throttlemap_lookup = 'throttle.csv'
lean_angle_lookup = 'lean_IOM_video_data.csv'
corner_radius_lookup = 'pikespeakradius.csv'
chain_eff_lookup = 'chain_eff_30kW.csv'

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

lateral_acc = np.zeros((steps+1,tests),dtype=float)

#Lookups
#soc to voltage
n = np.loadtxt(soc_to_voltage_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
x = n[:,0].astype(np.float)
y = n[:,1].astype(np.float)
soctovoltage_lookup = interp1d(x,y)

#distance to speed
n = np.loadtxt(dist_to_speed_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
x = n[:,0].astype(np.float)
y = n[:,1].astype(np.float)
distancetospeed_lookup = interp1d(x,y)

#distance to altitude 
n = np.loadtxt(dist_to_alt_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
x = n[:,0].astype(np.float)
y = n[:,1].astype(np.float)
distancetoaltitude_lookup = interp1d(x,y)

#rpm to top current % throttlemap
n = np.loadtxt(throttlemap_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
x = n[:,0].astype(np.float)
y = n[:,1].astype(np.float)
throttlemap = interp1d(x,y)

#distance to lean angle lookup
n = np.loadtxt(lean_angle_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
x = n[:,0].astype(np.float)
y = n[:,1].astype(np.float)
lean_angle_lookup = interp1d(x,y)

#distance to lean angle lookup
n = np.loadtxt(corner_radius_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
x = n[:,0].astype(np.float)
y = n[:,1].astype(np.float)
cornerradius = interp1d(x,y)

#motorcontroller efficiency 
#[volts_rms][amps_rms] to efficiency %
n = np.loadtxt(motor_controller_eff_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
x = n[:,0].astype(np.float)
y = n[:,1].astype(np.float)
z = n[:,2].astype(np.float)
points = np.transpose(np.array([x,y]))
values = np.array(z)
grid_x, grid_y = np.mgrid[np.min(x):np.max(x)+1, np.min(y):np.max(y)+1]
motor_controller_eff_grid = griddata(points, values, (grid_x, grid_y), method='linear')

#motor efficiency 
#[rpm][torque] to efficiency %
n = np.loadtxt(motor_eff_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
x = n[:,0].astype(np.float)
y = n[:,1].astype(np.float)
z = n[:,2].astype(np.float)
points = np.transpose(np.array([x,y]))
values = np.array(z)
grid_x, grid_y = np.mgrid[np.min(x):np.max(x)+1, np.min(y):np.max(y)+1]
motor_eff_grid = griddata(points, values, (grid_x, grid_y), method='linear')

#chain efficiency
#rpm to chain efficiency %
n = np.loadtxt(chain_eff_lookup,dtype = 'string',delimiter = ',', skiprows = 1)
x = n[:,0].astype(np.float)
y = n[:,1].astype(np.float)
chain_efficiency = interp1d(x,y)


#Make sure parameters don't extend lookups
if np.max(distancetospeed_lookup.x) < max_distance_travel:
    max_distance_travel =  np.max(distancetospeed_lookup.x)  
    print 'max_distance_travel greater than speed to distance look up'
    print 'max_distance_travel changed to ' + repr(max_distance_travel)


if np.max(distancetoaltitude_lookup.x) < max_distance_travel:
    max_distance_travel =  np.max(distancetoaltitude_lookup.x)  
    print 'max_distance_travel greater than altitude to distance look up'
    print 'max_distance_travel changed to ' + repr(max_distance_travel)

if np.max(cornerradius.x) < max_distance_travel:
    max_distance_travel =  np.max(cornerradius.x)  
    print 'max_distance_travel greater than cornerradius to distance look up'
    print 'max_distance_travel changed to ' + repr(max_distance_travel)

if np.max(lean_angle_lookup.x) < max_distance_travel:
    max_distance_travel =  np.max(lean_angle_lookup.x)  
    print 'max_distance_travel greater than lean angle to distance look up'
    print 'max_distance_travel changed to ' + repr(max_distance_travel)

if np.max(throttlemap.x) < top_rpm:
    top_rpm =  np.max(throttlemap.x) 
    print 'top rpm is greater than throttle map look up'
    print 'top rpm ' + repr(top_rpm)

if np.max(chain_efficiency.x) < top_rpm:
    top_rpm = np.max(chain_efficiency.x)
    print 'top rpm is greater than the chain efficiency look up'
    print 'top rpm ' + repr(top_rpm)    
    
(x,y) = motor_eff_grid.shape
if y-1 <  top_torque:
    top_torque = y-1
    top_motor_current = (y-1)/motor_torque_constant 
    print 'top_torque greater than motor efficiency look up'
    print 'top_motor_current changed to ' + repr(top_motor_current)

if x-1 <  top_rpm:
    top_rpm = x-1
    print 'top_rpm greater than motor efficiency look up'
    print 'top_rpm changed to ' + repr(top_rpm)

(x,y) = motor_controller_eff_grid.shape
if y-1 <  top_torque/motor_torque_constant:
    top_torque = (y-1) * motor_torque_constant
    top_motor_current = y-1
    print 'possible arms (from top motor current and motor torque constant) is greater than motor controller efficiency look up'
    print 'top_motor_current changed to ' + repr(top_motor_current)

if x-1 <  (top_rpm/(motor_rpm_constant)*(1/(sqrt2))) :
    top_rpm = (x-1)*(motor_rpm_constant)*(1/(sqrt2)) 
    print 'possible Vrms (from top_rpm and motor rpm constant) is greater than motor controller efficiency look up'
    print 'top_rpm changed to ' + repr(top_rpm)
    
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
    if motor_torque[n+1] > top_force[n+1]:
        return float('nan')
    arms[n+1] = motor_torque[n+1]/motor_torque_constant
    vrms[n+1] = motor_rpm[n+1]/(motor_rpm_constant)*(1/(sqrt2))  

    motor_efficiency[n+1] = motor_eff_grid[np.int(np.around(motor_rpm[n+1]))][np.int(np.around(motor_torque[n+1]))]
    motor_controller_efficiency[n+1] = motor_controller_eff_grid[np.int(np.around(vrms[n+1]))][np.int(np.around(arms[n+1]))]
    
    chain_power[n+1] = (p/(chain_efficiency(motor_rpm[[n+1]])))
    motor_power[n+1] = (chain_power[n+1]/(motor_efficiency[n+1]))
    motor_controller_power[n+1] = (motor_power[n+1]/(motor_controller_efficiency[n+1]))
    battery_power[n+1] = (motor_controller_power[n+1]/(battery_efficiency))
    
    motor_loss[n+1] = motor_power[n+1]*(1-motor_efficiency[n+1])
    motor_controller_loss[n+1] = motor_controller_power[n+1]*(1-motor_controller_efficiency[n+1])
    chain_loss[n+1] = chain_power[n+1]*(1-chain_efficiency(motor_rpm[n+1]))
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
    return max([0,((wheel_radius[n+1]*2*np.pi* (top_rpm) / (gearing))/60)])
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
    if Efficiency(s,f,p,n) == float('nan'):
        return max_motor_temp
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
        if (distance[n+1] > max_distance_travel) or speed[n] == 0:            
            return n                                #stop if cross finish line
        
        wheel_radius[n+1] = Wheel_Radius(lean_angle_lookup(distance[n+1]), n)
        
        voltage[n+1] = Battery_Voltage(n)           #find battery voltage
        top_force[n+1] = Top_force(n)               #Top_force at this point
        top_speed[n+1] = Top_speed(n)               #Top_speed at this point
        top_power[n+1] = Top_power(n)               #Top_power at this point
        
                                                    #Find lookup speed
        l_speed[n+1] = distancetospeed_lookup(distance[n+1])
        
        if l_speed[n+1] > top_speed[n+1]:           #Limit speed to top speed
            motor_rpm_limit[n+1] = 1
            t_speed[n+1] = top_speed[n+1]
        else:
            t_speed[n+1] = l_speed[n+1]
            
        
        c_force[n+1] = Force(t_speed[n+1],n)        
        
        if c_force[n+1] > top_force[n+1]:           #Limit speed to top force
            motor_torque_limit[n+1] = 1
            p_speed[n+1] = max([0,(opt.fsolve(force_solve,t_speed[n+1],n))[0]])
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
            mt_speed[n+1] = max([0,(opt.fsolve(power_solve,p_speed[n+1],n))[0]])
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
            speed[n+1] = (opt.fmin_tnc(Motor_Thermal_solve,mt_speed[n+1],args = (n,),bounds=bnds, approx_grad = True,messages = 0))[0]
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
        
        lateral_acc[n+1] =  speed[n+1]**2/cornerradius(distance[n+1])
        
    return steps
   #plot each loop here


   
#simulate and plot

n = 0
end = loop(n)
n+=1

print 'finish time (s) = ' + repr(time[end][0])
print 'max mph = ' + repr(np.max(speed[:end])*2.23)
print 'average mph = ' + repr(np.mean(speed[:end])*2.23)
print 'average power = ' + repr(np.mean(power[:end]))
print 'max power = ' + repr(np.max(power[:end]))
print 'energy = ' + repr(np.max(energy))
print 'amphour = ' + repr(np.max(amphour))
print 'max lateral acceleration = ' + repr(np.nanmax(lateral_acc))
print '% motor rpm limit  = ' + repr(np.mean(motor_rpm_limit[:end])*100)
print '% motor torque limit  = ' + repr(np.mean(motor_torque_limit[:end])*100)
print '% motor power limit  = ' + repr(np.mean(motor_power_limit[:end])*100)
print '% battery power limit  = ' + repr(np.mean(batt_power_limit[:end])*100)
print '% motor thermal limit = ' + repr(np.mean(motor_thermal_limit[:end])*100)
print '% motor lean angle limit = ' + repr(np.mean(lean_angle_limit[:end])*100)

#finish plot

    