# -*- coding: utf-8 -*-
"""
Created on Thu Aug 01 15:15:01 2013

@author: Sean
"""

import numpy as np

def FileToParams(fileName):
    
    data = np.loadtxt(open(fileName, "rb"), dtype = 'string', delimiter=',')
            #Allows user to enter either .txt or .csv file (Path needs \\ directories)
            #Example filename: "C:\\Python27\\example.txt" or "C:\\Python27\\example.csv"
            #Using only '\' will result in error for .csv files
    params = data[0]    #Creates array of params and inputs
    data = data[1:]     #Creates array of data without headers
    
    inputDict = dict()

    for index in range(len(params)):
        inputDict[params[index]] = data[:,index]    #Assigns data in same column as header
                                                    #to dict where key is header and data
                                                    #is the value linked to key
    
    for category in params: #Removes all missing data from dict values
        elementIndex = 0;
        for element in (inputDict[category]):
            if (not element):       #If element is empty ''
                inputDict[category] = np.delete(inputDict[category], elementIndex)
            else:
                elementIndex += 1
        inputDict[category] = inputDict[category].astype(np.float) #Converts to float

    print inputDict