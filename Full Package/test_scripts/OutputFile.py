# -*- coding: utf-8 -*-
"""
Created on Thu Aug 01 17:46:51 2013

@author: Sean
"""
import numpy as np

def OutputFile(fileName, outputDict):
    
    paramHeaders = np.array(outputDict.keys())  #Turns headers into numpy array
    values = np.zeros((len(outputDict[paramHeaders[0]]),len(paramHeaders)))
            #Creates an "empty" array with the total number of data points
    for x in range(len(paramHeaders)):
        currentValues = outputDict[paramHeaders[x]] #Gets list of header values
        currentValues = np.asarray(currentValues)   #Turns list into numpy array
        values[:,x] = currentValues #Plugs currentValues into "empty" array

    values.astype(str)  #Turns all floats into strings
    data = np.vstack((paramHeaders, values))    #Combines headers with values
    np.savetxt(fileName, data, delimiter=",", fmt="%s")
    print("Data transfer to " + fileName + " complete")