# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 20:10:55 2013

@author: Sean
"""
import os
import numpy as np
import Simulation as sim

def dependencies_for_automation():  #Missing imports needed to convert to .exe
    from scipy.sparse.csgraph import _validation

def FileToParams(inFiles):
    
    optionsFile = inFiles
    os.chdir(os.path.dirname(os.path.realpath(inFiles)))    
    
    inFiles = np.loadtxt(open(inFiles, "rb"), dtype = 'string', delimiter = ',')
    files = inFiles[1:,0]
    inputDict = dict()
    
    completedTransfers = 1
    for file in files:  #For each file, create a dictionary out of data
        fileName = file
        
        try:
            data = np.loadtxt(open(fileName, "rb"), dtype = 'string', delimiter=',')
                #Extracts all data from file into variable data
        except IOError:
            raise Exception("File in " + optionsFile + " not found.  Please remove entry or place file in same folder")
            
        fileName = inFiles[completedTransfers,1]      
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
                    
            try: #Try to convert to float, otherwise don't change
                fileDict[category] = fileDict[category].astype(np.float) 
            except:
                pass

        inputDict[fileName] = fileDict
        completedTransfers += 1
    
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

        ### NEEDS MORE TESTING ###        
        maxColumnLength = 0
        for x in paramHeaders:
            if maxColumnLength < np.size(currentDict[x]):
                maxColumnLength = np.size(currentDict[x])
        ### END OF TESTING ZONE ###
                
        values = np.zeros((maxColumnLength,len(paramHeaders)))
                #Creates an "empty" array with the total number of data points
        for x in range(len(paramHeaders)):
            currentValues = currentDict[paramHeaders[x]] #Gets list of header values
            currentValues = np.asarray(currentValues)   #Turns list into numpy array
            values[:,x] = currentValues #Plugs currentValues into "empty" array
    
        values.astype(str)  #Turns all floats into strings
        data = np.vstack((paramHeaders, values))    #Combines headers with values
        np.savetxt(fileName, data, delimiter=",", fmt="%s")
        print("Data transfer to " + fileName + " complete")


print
print
print

while True:   
    try:
        options = raw_input("Enter full path to options file: ")
        if os.path.exists(options):
            break
        else:
            print "File not found. Please enter a new file path"
    except:
        pass
        
dictionary = FileToParams(options)

#Pass dictionary to simulation, gets a new dictionary in return
dictionary = sim.Simulation(dictionary)

outputDirectory = raw_input("Enter full path folder directory for out files: ")
OutputFile(outputDirectory, dictionary)
