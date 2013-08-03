# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 20:10:55 2013

@author: Sean
"""
import os, glob
import numpy as np

def FileToParams(folderDirectory):
    
    files = []
    inputDict = dict()
    os.chdir(folderDirectory)
    for file in glob.glob("*.csv"): #Find all .csv files, add to total files
        files.append(file)
    for file in glob.glob("*.txt"): #Find all .txt files add to total files
        files.append(file)
    
    for file in files:  #For each file, create a dictionary out of data
        fileName = file
        
        data = np.loadtxt(open(fileName, "rb"), dtype = 'string', delimiter=',')
                #Extracts all data from file into variable data
        
        params = data[0]    #Creates array of params and inputs
        data = data[1:]     #Creates array of data without headers        
        fileDict = dict()
    
        for index in range(len(params)):
            fileDict[params[index]] = data[:,index]    #Assigns data in same column as header
                                                        #to dict where key is header and data
                                                        #is the value linked to key
        
        for category in params: #Removes all missing data from dict values
            elementIndex = 0;
            for element in (fileDict[category]):
                if (not element):       
                    fileDict[category] = np.delete(fileDict[category], elementIndex)
                else:
                    elementIndex += 1
            fileDict[category] = fileDict[category].astype(np.float) #Converts to float

        inputDict[fileName] = fileDict
    
    return inputDict
    
    
       
def OutputFile(folderName, outputDict):
    
    if not os.path.exists(folderName):  #Creates a new folder if it doesn't exist
        os.makedirs(folderName)
        
    if not folderName.endswith("\\"):   #Corrects folderName if needed
            folderName = folderName + "\\"
            
    fileNames = np.array(outputDict.keys())
    
    for key in fileNames:
            
        fileName = folderName + key
        currentDict = outputDict[key]
        
        paramHeaders = np.array(currentDict.keys())  #Turns headers into numpy array
        values = np.zeros((len(currentDict[paramHeaders[0]]),len(paramHeaders)))
                #Creates an "empty" array with the total number of data points
        for x in range(len(paramHeaders)):
            currentValues = currentDict[paramHeaders[x]] #Gets list of header values
            currentValues = np.asarray(currentValues)   #Turns list into numpy array
            values[:,x] = currentValues #Plugs currentValues into "empty" array
    
        values.astype(str)  #Turns all floats into strings
        data = np.vstack((paramHeaders, values))    #Combines headers with values
        np.savetxt(fileName, data, delimiter=",", fmt="%s")
        print("Data transfer to " + fileName + " complete")
            
def Simulation(dictionary):
    
    for file in dictionary:
        for key in dictionary[file]:
            for value in range(dictionary[file][key].size):
                dictionary[file][key][value] = dictionary[file][key][value] + 1
                
    return dictionary    
    
    
folderDirectory = input("Enter full path folder directory for in files: ")
dictionary = FileToParams(folderDirectory)

#Pass dictionary to simulation, gets a new dictionary in return
dictionary = Simulation(dictionary)

outputDirectory = input("Enter full path folder directory for out files: ")
OutputFile(outputDirectory, dictionary)
