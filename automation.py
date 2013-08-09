# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 20:10:55 2013

@author: Sean
"""

import logging
import os
import numpy as np
import Simulation as sim

def dependencies_for_automation():  #Missing imports needed to convert to .exe
    from scipy.sparse.csgraph import _validation

def FileToParams(inFiles):
    
    logging.info("STARTING FUNCTIONS FileToParams")
    os.chdir(os.path.dirname(os.path.realpath(inFiles)))    
    
    inFiles = np.loadtxt(open(inFiles, "rb"), dtype = 'string', delimiter = ',')
    files = inFiles[1:,0]
    inputDict = dict()
    
    completedTransfers = 1
    for file in files:  #For each file, create a dictionary out of data
        
        logging.info("Current file to search for data: %s",file)
        fileName = file
        
        try:
            data = np.loadtxt(open(fileName, "rb"), dtype = 'string', delimiter=',')
            logging.info("Data extraction from %s complete", file)
                #Extracts all data from file into variable data
        except IOError:
            logging.critical("Unable to load %s",file)
            raise Exception("File " + fileName + " not found.  Please remove entry or place file in same folder")
            
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
    
    logging.info("Files have been converted to dictionaries")
    return inputDict
    
    
       
def OutputFile(folderName, outputDict):
    

    logging.info("STARTING FUNCTION OutputFile")        
    fileNames = np.array(outputDict.keys())
    
    for key in fileNames:
        
        logging.info("Converting dictionary %s to file",key)
        fileName = folderName + key
        logging.debug("File will be saved at %s",fileName)
        currentDict = outputDict[key]
        
        
        paramHeaders = np.array(currentDict.keys())  #Turns headers into numpy array

       
        maxColumnLength = 0 #Find maximum number of rows
        for x in paramHeaders:
            if maxColumnLength < np.size(currentDict[x]):
                maxColumnLength = np.size(currentDict[x])

        values = np.ma.zeros((maxColumnLength,len(paramHeaders)))
                #Creates an "empty" array with the total number of data points

        
        for x in range(len(paramHeaders)):
            currentValues = currentDict[paramHeaders[x]] #Gets list of header values
               #Turns list into numpy array

            if np.ndim(currentValues) > 1:
                currentValues = np.asarray(currentValues)
                values[:,x] = currentValues[:,0] #Plugs currentValues into "empty" array
            else:
                values[0,x] = currentValues
                values[:,x] = np.ma.masked_less_equal(values[:,x],0.1)
        
    
        data = np.ma.vstack((paramHeaders, values))    #Combines headers with values
        try:
            np.savetxt(fileName, data, delimiter=",", fmt="%s")
        except IOError:
            logging.critical("Unable to save %s",fileName)
            raise Exception("Unable to save file")
            
        print("Data transfer to " + fileName + " complete")
        logging.info("Data converted and saved to %s", fileName)

print
print
print

logging.basicConfig(filename="BCS_log.txt",format='%(asctime)s - %(levelname)s - %(message)s',level=logging.DEBUG)
#
logging.info("STARTING automation.py")

while True: #Make sure user input points to a file
    try:
        options = raw_input("Enter full path to options file: ")
        logging.debug("Entered path: %s", options)
        if os.path.isfile(options):
            logging.info("Path to options file is valid")
            break
        else:
            print "File not found. Please enter a new file path"
            logging.warning("%s is invalid",options)
    except:
        pass
    
while True: #Make sure user input points to a writable (or possible) folder
    try:
        outputDirectory = raw_input("Enter full path folder directory for out files: ")
        logging.debug("Entered out path: %s",outputDirectory)
        
        if not os.path.exists(outputDirectory):  #Creates a new folder if it doesn't exist
            os.makedirs(outputDirectory)
            logging.info("Created new directory")
            
        if not outputDirectory.endswith("\\"):   #Corrects directory if needed
            outputDirectory = outputDirectory + "//"
            logging.info("Modified input to %s",outputDirectory)
            
        np.savetxt((outputDirectory + "test.txt"), np.array([0]), delimiter=",", fmt="%s")
        os.remove(outputDirectory + "test.txt")
        break
    
    except:
        print "Directory can't be created or is not writable. Enter a new path"
        logging.warning("User output path invalid")

dictionary = FileToParams(options)
#Pass dictionary to simulation, gets a new dictionary in return
dictionary = sim.Simulation(dictionary)
OutputFile(outputDirectory, dictionary)
logging.info("ENDING automation.py" + os.linesep + os.linesep)
logging.shutdown()
