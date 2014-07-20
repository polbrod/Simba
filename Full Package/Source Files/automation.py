# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 20:10:55 2013

@author: Sean Harrington
"""

import logging
import os
import numpy as np
import Simulation as sim
import win32com.client
import wx
import wx.grid as gridlib
import wx.lib.scrolledpanel as scrolled
import wx.lib.masked as mask
import wx.lib.customtreectrl as ct
import collections
import shutil
import wx.richtext
from operator import itemgetter
from threading import Thread

from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub
from copy import deepcopy
from datetime import datetime

import sys, subprocess
import traceback

closeWorkerThread = 0

def dependencies_for_automation():  #Missing imports needed to convert to .exe
    from scipy.sparse.csgraph import _validation


def SensitivityAnalysis(dictionary, sensitivityValue):  

    global closeWorkerThread
    parameterDict = collections.OrderedDict()
    
    # Take any file since they all have the same input parameters
    for key in dictionary[dictionary.keys()[0]]:
        if not isinstance(dictionary[dictionary.keys()[0]][key][0],basestring):
            outputFiles = []
            originalDictionary = deepcopy(dictionary)
            
            # Plus x% from the current key in each file
            for file in dictionary:
                originalData = dictionary[file][key]
                
                # Probably a bad solution to allow for the renaming of keys...
                dictionary[file][key] = originalData * (1.0 + sensitivityValue)
                
            outputFiles.append(sim.Simulation(dictionary))
            dictionary = deepcopy(originalDictionary)
            
            # Minus x% from the current key in each file
            for file in dictionary:
                originalData = dictionary[file][key]
                dictionary[file][key] = originalData * (1.0 - sensitivityValue)

            outputFiles.append(sim.Simulation(dictionary))
            dictionary = deepcopy(originalDictionary)
            parameterDict[key] = outputFiles
        else:
            for file in dictionary:
                i = 0
                while i < 6:
                    wx.CallAfter(pub.sendMessage, "update", "")
                    i += 1
        if closeWorkerThread == 1:
            return
        
    

    return parameterDict
    
def CreateSortArrays(dictionary):
    
    
    # Sorting lists
    # Should rename plus to largest
    sorting_arrays = dict()
    TS_plus_dict = collections.OrderedDict()
    # Should rename minus to smallest
    TS_minus_dict = collections.OrderedDict()
    TS_large_diff_dict = collections.OrderedDict()
    TS_small_diff_dict = collections.OrderedDict()
    TS_large_perc_diff_dict = collections.OrderedDict()
    TS_small_perc_diff_dict = collections.OrderedDict()
    
    AS_plus_dict = collections.OrderedDict()
    AS_minus_dict = collections.OrderedDict()
    AS_large_diff_dict = collections.OrderedDict()
    AS_small_diff_dict = collections.OrderedDict()
    AS_large_perc_diff_dict = collections.OrderedDict()
    AS_small_perc_diff_dict = collections.OrderedDict()
    
    TP_plus_dict = collections.OrderedDict()
    TP_minus_dict = collections.OrderedDict()
    TP_large_diff_dict = collections.OrderedDict()
    TP_small_diff_dict = collections.OrderedDict()
    TP_large_perc_diff_dict = collections.OrderedDict()
    TP_small_perc_diff_dict = collections.OrderedDict()
    
    AP_plus_dict = collections.OrderedDict()
    AP_minus_dict = collections.OrderedDict()
    AP_large_diff_dict = collections.OrderedDict()
    AP_small_diff_dict = collections.OrderedDict()
    AP_large_perc_diff_dict = collections.OrderedDict()
    AP_small_perc_diff_dict = collections.OrderedDict()
    
    E_plus_dict = collections.OrderedDict()
    E_minus_dict = collections.OrderedDict()
    E_large_diff_dict = collections.OrderedDict()
    E_small_diff_dict = collections.OrderedDict()
    E_large_perc_diff_dict = collections.OrderedDict()
    E_small_perc_diff_dict = collections.OrderedDict()    
    
    for file in dictionary['gearing'][0].keys():
        
        print 'File in sort arrays: '
        print file
        
        TS_plus_list = []
        TS_minus_list = []
        TS_diff_list = []
        TS_perc_diff_list = []
        AS_plus_list = []
        AS_minus_list = []
        AS_diff_list = []
        AS_perc_diff_list = []
        TP_plus_list = []
        TP_minus_list = []
        TP_diff_list = []
        TP_perc_diff_list = []
        AP_plus_list = []
        AP_minus_list = []
        AP_diff_list = []
        AP_perc_diff_list = []
        E_plus_list = []
        E_minus_list = []
        E_diff_list = []
        E_perc_diff_list = []
        
        
        for parameter in dictionary.keys():
            TS_plus_value = dictionary[parameter][0][file]['Max MPH']
            TS_plus_list.append((TS_plus_value,parameter))
            AS_plus_value = dictionary[parameter][0][file]['Average MPH']
            AS_plus_list.append((AS_plus_value,parameter))
            TP_plus_value = dictionary[parameter][0][file]['Max Power (Watts)']
            TP_plus_list.append((TP_plus_value,parameter))
            AP_plus_value = dictionary[parameter][0][file]['Average Power (Watts)']
            AP_plus_list.append((AP_plus_value,parameter))
            E_plus_value = dictionary[parameter][0][file]['Max Energy (Wh)']
            E_plus_list.append((E_plus_value,parameter))
            
            
            TS_minus_value = dictionary[parameter][1][file]['Max MPH']
            TS_minus_list.append((TS_minus_value,parameter))
            AS_minus_value = dictionary[parameter][1][file]['Average MPH']
            AS_minus_list.append((AS_minus_value,parameter))
            TP_minus_value = dictionary[parameter][1][file]['Max Power (Watts)']
            TP_minus_list.append((TP_minus_value,parameter))
            AP_minus_value = dictionary[parameter][1][file]['Average Power (Watts)']
            AP_minus_list.append((AP_minus_value,parameter))
            E_minus_value = dictionary[parameter][1][file]['Max Energy (Wh)']
            E_minus_list.append((E_minus_value,parameter))
            
            diff = abs(TS_plus_value - TS_minus_value)
            diffPercent = diff / (TS_plus_value + TS_minus_value)
            TS_diff_list.append((diff,parameter))
            TS_perc_diff_list.append((diffPercent,parameter))
            
            diff = abs(AS_plus_value - AS_minus_value)
            diffPercent = diff / (AS_plus_value + AS_minus_value)
            AS_diff_list.append((diff,parameter))
            AS_perc_diff_list.append((diffPercent, parameter))
            
            diff = abs(TP_plus_value - TP_minus_value)
            diffPercent = diff / (TP_plus_value + TP_minus_value)
            TP_diff_list.append((diff,parameter))
            TP_perc_diff_list.append((diffPercent,parameter))
            
            diff = abs(AP_plus_value - AP_minus_value)
            diffPercent = diff / (AP_plus_value + AP_minus_value)
            AP_diff_list.append((diff, parameter))
            AP_perc_diff_list.append((diffPercent, parameter))
            
            diff = abs(E_plus_value - E_minus_value)
            diffPercent = diff / (E_plus_value + E_minus_value)
            E_diff_list.append((diff, parameter))
            E_perc_diff_list.append((diffPercent, parameter))
      
              
      
        # Largest value first
        TS_plus_dict[file] = sorted(TS_plus_list, key=itemgetter(0), reverse = True)
        AS_plus_dict[file] = sorted(AS_plus_list, key=itemgetter(0), reverse = True)
        TP_plus_dict[file] = sorted(TP_plus_list, key=itemgetter(0), reverse = True)
        AP_plus_dict[file] = sorted(AP_plus_list, key=itemgetter(0), reverse = True)
        E_plus_dict[file] = sorted(E_plus_list, key=itemgetter(0), reverse = True)
        
        # Smallest value first
        TS_minus_dict[file] = sorted(TS_minus_list, key=itemgetter(0))
        AS_minus_dict[file] = sorted(AS_minus_list, key=itemgetter(0))
        TP_minus_dict[file] = sorted(TP_minus_list, key=itemgetter(0))
        AP_minus_dict[file] = sorted(AP_minus_list, key=itemgetter(0))
        E_minus_dict[file] = sorted(E_minus_list, key=itemgetter(0))
        
        # Largest diff first
        TS_large_diff_dict[file] = sorted(TS_diff_list, key=itemgetter(0), reverse = True)
        AS_large_diff_dict[file] = sorted(AS_diff_list, key=itemgetter(0), reverse = True)
        TP_large_diff_dict[file] = sorted(TP_diff_list, key=itemgetter(0), reverse = True)
        AP_large_diff_dict[file] = sorted(AP_diff_list, key=itemgetter(0), reverse = True)
        E_large_diff_dict[file] = sorted(E_diff_list, key=itemgetter(0), reverse = True)
        
        # Smallest diff first
        TS_small_diff_dict[file] = sorted(TS_diff_list, key=itemgetter(0))
        AS_small_diff_dict[file] = sorted(AS_diff_list, key=itemgetter(0))
        TP_small_diff_dict[file] = sorted(TP_diff_list, key=itemgetter(0))
        AP_small_diff_dict[file] = sorted(AP_diff_list, key=itemgetter(0))
        E_small_diff_dict[file] = sorted(E_diff_list, key=itemgetter(0))
        
        TS_large_perc_diff_dict[file] = sorted(TS_perc_diff_list, key=itemgetter(0), reverse = True)
        AS_large_perc_diff_dict[file] = sorted(AS_perc_diff_list, key=itemgetter(0), reverse = True)
        TP_large_perc_diff_dict[file] = sorted(TP_perc_diff_list, key=itemgetter(0), reverse = True)
        AP_large_perc_diff_dict[file] = sorted(AP_perc_diff_list, key=itemgetter(0), reverse = True)
        E_large_perc_diff_dict[file] = sorted(E_perc_diff_list, key=itemgetter(0), reverse = True)
    
        TS_small_perc_diff_dict[file] = sorted(TS_perc_diff_list, key=itemgetter(0))
        AS_small_perc_diff_dict[file] = sorted(AS_perc_diff_list, key=itemgetter(0))
        TP_small_perc_diff_dict[file] = sorted(TP_perc_diff_list, key=itemgetter(0))
        AP_small_perc_diff_dict[file] = sorted(AP_perc_diff_list, key=itemgetter(0))
        E_small_perc_diff_dict[file] = sorted(E_perc_diff_list, key=itemgetter(0))

    
    
    sorting_arrays["TS_large_dict"] = TS_plus_dict
    sorting_arrays["TS_small_dict"] = TS_minus_dict
    sorting_arrays["TS_large_diff_dict"] = TS_large_diff_dict
    sorting_arrays["TS_small_diff_dict"] = TS_small_diff_dict
    sorting_arrays["TS_large_perc_diff_dict"] = TS_large_perc_diff_dict
    sorting_arrays["TS_small_perc_diff_dict"] = TS_small_perc_diff_dict
    
    sorting_arrays["AS_large_dict"] = AS_plus_dict
    sorting_arrays["AS_small_dict"] = AS_minus_dict
    sorting_arrays["AS_large_diff_dict"] = AS_large_diff_dict
    sorting_arrays["AS_small_diff_dict"] = AS_small_diff_dict
    sorting_arrays["AS_large_perc_diff_dict"] = AS_large_perc_diff_dict
    sorting_arrays["AS_small_perc_diff_dict"] = AS_small_perc_diff_dict
    
    sorting_arrays["TP_large_dict"] = TP_plus_dict
    sorting_arrays["TP_small_dict"] = TP_minus_dict
    sorting_arrays["TP_large_diff_dict"] = TP_large_diff_dict
    sorting_arrays["TP_small_diff_dict"] = TP_small_diff_dict
    sorting_arrays["TP_large_perc_diff_dict"] = TP_large_perc_diff_dict
    sorting_arrays["TP_small_perc_diff_dict"] = TP_small_perc_diff_dict
    
    sorting_arrays["AP_large_dict"] = AP_plus_dict
    sorting_arrays["AP_small_dict"] = AP_minus_dict
    sorting_arrays["AP_large_diff_dict"] = AP_large_diff_dict
    sorting_arrays["AP_small_diff_dict"] = AP_small_diff_dict
    sorting_arrays["AP_large_perc_diff_dict"] = AP_large_perc_diff_dict
    sorting_arrays["AP_small_perc_diff_dict"] = AP_small_perc_diff_dict
    
    sorting_arrays["E_large_dict"] = E_plus_dict
    sorting_arrays["E_small_dict"] = E_minus_dict
    sorting_arrays["E_large_diff_dict"] = E_large_diff_dict
    sorting_arrays["E_small_diff_dict"] = E_small_diff_dict
    sorting_arrays["E_large_perc_diff_dict"] = E_large_perc_diff_dict
    sorting_arrays["E_small_perc_diff_dict"] = E_small_perc_diff_dict
    
    
    
    return sorting_arrays
        
    
def ProjectToParams(inFiles):
    
    optionsFile = inFiles
    logging.info("STARTING FUNCTIONS FileToParams")
    os.chdir(os.path.dirname(os.path.realpath(inFiles)))    
    logging.debug("Options file location passed: %s", inFiles)
    inFiles = np.loadtxt(open(inFiles, "rb"), dtype = 'string', delimiter = ',')
    files = inFiles[1:,0]
    wx.CallAfter(pub.sendMessage, "InputFiles", files)
    inputDict = collections.OrderedDict()
    
    completedTransfers = 1
    for file in files:  #For each file, create a dictionary out of data
        
        logging.info("Current file to search for data: %s",file)
        fileName = file
        emptyFile = False #Initalize for possible of empty file
        
        try:
            data = np.loadtxt(open(fileName, "rb"), dtype = 'string', delimiter=',')
            if np.shape(data) == (0,):
                emptyFile = True
            logging.info("Data extraction from %s complete", file)
                #Extracts all data from file into variable data
        except IOError:
            logging.critical("Unable to load %s",file)
            GUIdialog = wx.MessageDialog(None, "Unable to load file in " + optionsFile +". Make sure "+ optionsFile + " is correct or specify a new options file", "Error", wx.OK)
            GUIdialog.ShowModal()
            GUIdialog.Destroy()
            raise Exception("File " + fileName + " not found.  Please remove entry or place file in same folder")
            
            
        fileDict = collections.OrderedDict()
        if not emptyFile:
            fileName = inFiles[completedTransfers,1]      
            params = data[0]    #Creates array of params and inputs
            data = data[1:]     #Creates array of data without headers        
        
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
        fileName = folderName + "\\" + key
        logging.debug("File will be saved at %s", fileName)
        currentDict = outputDict[key]
        
        paramHeaders = np.array(currentDict.keys())  #Turns headers into numpy array

        maxColumnLength = 0 #Find maximum number of rows
        for x in paramHeaders:
            if maxColumnLength < np.size(currentDict[x]):
                maxColumnLength = np.size(currentDict[x])

        values = np.ma.zeros((maxColumnLength,len(paramHeaders)))
                #Creates an "empty" array with the total number of data points

        
        for x in range(len(paramHeaders)):
            currentValues = currentDict[paramHeaders[x]]#Gets list of header values
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
            GUIdialog = wx.MessageDialog(None, "Unable to save file to " + fileName +". Make sure "+ fileName + " is closed, specify a new file to save to, or pick a save directory that's writable.", "Error", wx.OK)
            GUIdialog.ShowModal()
            GUIdialog.Destroy()            
            raise Exception("Unable to save file")
            
        print("Data transfer to " + fileName + " complete")
        logging.info("Data converted and saved to %s", fileName)


def SaveInput(folderName, outputDict):
    
    logging.info("STARTING FUNCTION SaveInput")        
    fileNames = np.array(outputDict.keys())
    
    for key in fileNames:
        
        logging.info("Converting dictionary %s to file",key)
        fileName = folderName + "\\" + key
        logging.debug("File will be saved at %s", fileName)
        currentDict = outputDict[key]
        
        paramHeaders = np.array(currentDict.keys())  #Turns headers into numpy array

        maxColumnLength = 0 #Find maximum number of rows
        for x in paramHeaders:
            if maxColumnLength < np.size(currentDict[x]):
                maxColumnLength = np.size(currentDict[x])

        values = np.zeros((maxColumnLength,len(paramHeaders)), dtype = '|S50')
                #Creates an "empty" array with the total number of data points

        
        for x in range(len(paramHeaders)):
            try:
                currentValues = str(currentDict[paramHeaders[x]][0]) #Gets list of header values
                   #Turns list into numpy array
                
    
                values[0,x] = currentValues       
            except:
                pass            
        data = np.vstack((paramHeaders, values))    #Combines headers with values
        try:
            np.savetxt(fileName, data, delimiter=",", fmt="%s")
        except IOError:
            logging.critical("Unable to save %s",fileName)
            GUIdialog = wx.MessageDialog(None, "Unable to save file to " + fileName +". Make sure "+ fileName + " is closed, specify a new file to save to, or pick a save directory that's writable.", "Error", wx.OK)
            GUIdialog.ShowModal()
            GUIdialog.Destroy()            
            raise Exception("Unable to save file")
            
        print("Data transfer to " + fileName + " complete")
        logging.info("Data converted and saved to %s", fileName)
    
    
def WriteFolder(optionsFile, folderName):
    
    try:
        data = np.loadtxt(open(optionsFile, "rb"), dtype = "|S256", delimiter=',')
        logging.info("Data extraction from %s complete", file)
                #Extracts all data from file into variable data
    except IOError:
        logging.critical("Unable to load %s",file)
        GUIdialog = wx.MessageDialog(None, "Unable to edit " + optionsFile +". Make sure "+ optionsFile + " is correct or specify a new options file", "Error", wx.OK)
        GUIdialog.ShowModal()
        GUIdialog.Destroy()
        raise Exception("File " + optionsFile + " not found")
      

    if np.shape(data)[1] <= 4:
        newArray = np.zeros((np.shape(data)[0],2), dtype = "|S256")
        newArray[0] = "Output Folder"
        newArray[1] = folderName
        data = np.concatenate((data, newArray), axis=1)
    else:
        data[0,3] = "Output Folder"
        data[1,3] = folderName
        
    try:
        np.savetxt(optionsFile, data, delimiter=",", fmt="%s")
        logging.info("%s successfully edited", optionsFile)
    except:
        logging.info("%s NOT successfully edited", optionsFile)
    

##############################################################################
# GUI Starts Here
##############################################################################
        
###############################################################################
   
class PopupFrame(wx.Frame):
     def __init__(self):
         """Constructor"""
         wx.Frame.__init__(self, None, title="New Project Name", size=(300,120), style = wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN)
           
         panel = wx.Panel(self)
           
         text = wx.StaticText(panel, label="Enter the new project name")
         self.projectName = wx.TextCtrl(panel, size = (280, -1))
         OKButton = wx.Button(panel, label = "OK")
         CancelButton = wx.Button(panel, label = "Cancel")
          
         panel.Bind(wx.EVT_BUTTON, self.OnOK, OKButton)
         panel.Bind(wx.EVT_BUTTON, self.OnCancel, CancelButton)
    
         horizontalSizer = wx.BoxSizer(wx.HORIZONTAL)
         horizontalSizer.AddSpacer(65)
         horizontalSizer.Add(OKButton, 0, wx.ALL, border = 5)
         horizontalSizer.Add(CancelButton, 0, wx.ALL, border= 5)

    
         panelSizer = wx.BoxSizer(wx.VERTICAL)
         panelSizer.Add(text, 0, wx.ALL, border=5)
         panelSizer.Add(self.projectName, 0, wx.ALL, border=5)
         panelSizer.Add(horizontalSizer)
         panel.SetSizer(panelSizer)
         panel.Fit()
           
     def OnOK(self, event):
         wx.CallAfter(pub.sendMessage, "ProjectName", self.projectName.GetValue())
         self.Destroy()
     def OnCancel(self, event):
         wx.CallAfter(pub.sendMessage, "ProjectName", "Cancel")
         self.Destroy()
          
     
class IOSplitterPanel(wx.Panel):
    """ Constructs a Vertical splitter window with left and right panels"""
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        splitter = wx.SplitterWindow(self, style = wx.SP_3D| wx.SP_LIVE_UPDATE)
        
        #splitter.SetSashPosition(100)
        splitter.SetMinimumPaneSize(20)
        #leftPanel = InputPanel(splitter, style = wx.BORDER_SIMPLE | wx.TAB_TRAVERSAL)
        statusPanel = StatusPanel(splitter, style = wx.BORDER_SIMPLE)
        rightPanel = OutputPanel(splitter, style = wx.BORDER_SIMPLE)        

        splitter.SplitHorizontally(rightPanel, statusPanel) 
        PanelSizer=wx.BoxSizer(wx.VERTICAL)
        PanelSizer.Add(splitter, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(PanelSizer)
        splitter.SetSashPosition(800)


########################################################################

class SensitivityAnalysisFrame(wx.Frame):
    """Constructor"""
    #----------------------------------------------------------------------
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, title="Sensitivity Analysis Results", size = (1200,800))
                
        ################################################################
        # Define mainsplitter as child of Frame and add IOSplitterPanel and StatusPanel as children
        mainsplitter = wx.SplitterWindow(self, style = wx.SP_3D| wx.SP_LIVE_UPDATE)
        #mainsplitter.SetSashGravity(0.2)
        mainsplitter.SetMinimumPaneSize(20)

        #splitterpanel = IOSplitterPanel(mainsplitter)
        #statusPanel = StatusPanel(mainsplitter, style = wx.BORDER_SIMPLE)
        leftPanel = OptionsPanel(mainsplitter, style = wx.BORDER_SIMPLE | wx.TAB_TRAVERSAL)
        rightPanel = SAResultsPanel(mainsplitter, style = wx.BORDER_SIMPLE | wx.TAB_TRAVERSAL)

        mainsplitter.SplitVertically(leftPanel, rightPanel)
        windowW, windowH = wx.DisplaySize()
        mainsplitter.SetSashPosition(300, True)
        newW = windowW/0.6
        #mainsplitter.SetSashPosition(windowW - newW, True)
        #mainsplitter.SetSashPosition(-50, True)
        MainSizer = wx.BoxSizer(wx.VERTICAL)
        MainSizer.Add(mainsplitter, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(MainSizer)
        #################################################################        
        self.Refresh()

        
class OptionsPanel(scrolled.ScrolledPanel):
    """Left panel in WIP GUI window that manages all the sorting and filtering"""
    def __init__(self, parent, *args, **kwargs):
        scrolled.ScrolledPanel.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.fillSizer = True
        self.SADict = collections.OrderedDict()
        self.sortArrays = collections.OrderedDict()
        pub.subscribe(self.TransferSortArrays, ("TransferSortArrays"))
        pub.subscribe(self.TransferSADict, ("TransferSADictionary")) 
        
        self.rightPanel = wx.Panel(self)
        #Create Sizers    
        
        #self.hSizer.AddSpacer(20)
        self.inputs = []
        self.outputs = []
        self.vSizer = wx.BoxSizer(wx.VERTICAL)
        self.vSizer1 = wx.BoxSizer(wx.VERTICAL)
        self.hSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hSortSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD)
        
        self.vSizer.AddSpacer(5)
        self.optionsText = wx.StaticText(self, wx.ID_ANY, "   Toggle variables to display")
        self.optionsText.SetFont(font)
        self.vSizer.Add(self.optionsText)
        self.vSizer.AddSpacer(5)
        self.sortText = wx.StaticText(self, wx.ID_ANY, "   Sorting options")
        self.sortText.SetFont(font)
        
        self.rightSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.topSpeedItem = wx.RadioButton(self, -1, label='Top Speed', style=wx.RB_GROUP)
        self.rightSizer.Add(self.topSpeedItem)
        self.averageSpeedItem = wx.RadioButton(self, -1, label='Average Speed')
        self.rightSizer.Add(self.averageSpeedItem)
        self.topPowerItem = wx.RadioButton(self, -1, label='Top Power')
        self.rightSizer.Add(self.topPowerItem)
        self.averagePowerItem = wx.RadioButton(self, -1, label='Average Power')
        self.rightSizer.Add(self.averagePowerItem)
        self.energyItem = wx.RadioButton(self, -1, label='Energy')
        self.rightSizer.Add(self.energyItem)
        self.rightSizer.AddSpacer(10)
        self.largest2Smallest = wx.RadioButton(self, -1, label='Largest to Smallest', style=wx.RB_GROUP)
        self.rightSizer.Add(self.largest2Smallest)
        self.smallest2Largest = wx.RadioButton(self, -1, label='Smallest to Largest')
        self.rightSizer.Add(self.smallest2Largest)
        self.smallestDiff = wx.RadioButton(self, -1, label='Smallest Difference')
        self.rightSizer.Add(self.smallestDiff)
        self.largestDiff = wx.RadioButton(self, -1, label='Largest Difference')
        self.rightSizer.Add(self.largestDiff)
        self.smallestPerc = wx.RadioButton(self, -1, label='Smallest Percent Difference')
        self.rightSizer.Add(self.smallestPerc)
        self.largestPerc = wx.RadioButton(self, -1, label='Largest Percent Difference')
        self.rightSizer.Add(self.largestPerc)
        
        self.offsetSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.offsetSizer.AddSpacer(14)
        self.offsetSizer.Add(self.rightSizer)
        
        self.Bind(wx.EVT_RADIOBUTTON, self.Sort, self.topSpeedItem)
        self.Bind(wx.EVT_RADIOBUTTON, self.Sort, self.averageSpeedItem)
        self.Bind(wx.EVT_RADIOBUTTON, self.Sort, self.topPowerItem)
        self.Bind(wx.EVT_RADIOBUTTON, self.Sort, self.averagePowerItem)
        self.Bind(wx.EVT_RADIOBUTTON, self.Sort, self.energyItem)
        
        self.Bind(wx.EVT_RADIOBUTTON, self.Sort, self.largest2Smallest)
        self.Bind(wx.EVT_RADIOBUTTON, self.Sort, self.smallest2Largest)
        self.Bind(wx.EVT_RADIOBUTTON, self.Sort, self.smallestDiff)
        self.Bind(wx.EVT_RADIOBUTTON, self.Sort, self.largestDiff)
        self.Bind(wx.EVT_RADIOBUTTON, self.Sort, self.smallestPerc)
        self.Bind(wx.EVT_RADIOBUTTON, self.Sort, self.largestPerc)
        
        self.SetSizer(self.vSizer)
        #self.vSizer.Fit(self)
        #self.SetAutoLayout(1)
        self.SetupScrolling(scroll_x = False, scroll_y = True, rate_x=20, rate_y=20, scrollToTop=True)
        
    def TransferSADict(self, msg):
        self.SADict = msg.data
       
        for key in self.SADict.keys():
            trigger = wx.CheckBox(self, wx.ID_ANY, label = key)
            trigger.SetValue(True)
            self.outputs.append(key)
            self.Bind(wx.EVT_CHECKBOX, self.configureOutput, id = trigger.GetId())
            self.inputs.append(trigger)
        
        if self.fillSizer is True:
            for inputItem in self.inputs: 
                self.vSizer1.Add(inputItem, 0, wx.ALL, 1) 
            self.fillSizer = False
            
            
        wx.CallAfter(pub.sendMessage, "DisplayOutputs", self.outputs)
        self.hSizer1.AddSpacer(15)
        self.hSizer1.Add(self.vSizer1)
        self.vSizer.Add(self.hSizer1)
        
        self.vSizer.AddSpacer(10)
        self.vSizer.Add(self.sortText)
        #self.vSizer.Add(self.leftPanel)
        self.vSizer.Add(self.offsetSizer)
        '''
        self.hSortSizer.Add(self.leftPanel, 1, wx.EXPAND)
        self.hSortSizer.AddSpacer(5)
        self.hSortSizer.Add(self.rightPanel, 1, wx.EXPAND)
        '''
        self.vSizer.Add(self.hSortSizer)

        #self.vSizer.Fit(self)
        self.Layout()
        
        #self.Layout()
        
    def TransferSortArrays(self, msg):
        self.sortArrays = msg.data
    
    def configureOutput(self, e):
        
        for cb in self.inputs:
            value = cb.GetValue()
            try:
                name = cb.GetLabel()
            except:
                print 'unable to get label'
                
            if value == True:
                if name not in self.outputs:
                    self.outputs.append(name)
            else:
                # If outputs doesn't contain name already, skip
                if name in self.outputs:
                    self.outputs.remove(name)
                
        wx.CallAfter(pub.sendMessage, "DisplayOutputs", self.outputs)
        
    def Sort(self, e):
        if self.topSpeedItem.GetValue() == True:
            if self.largest2Smallest.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "TS_large_dict")
            elif self.smallest2Largest.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "TS_small_dict")
            elif self.largestDiff.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "TS_large_diff_dict")
            elif self.smallestDiff.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "TS_small_diff_dict")
            elif self.largestPerc.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "TS_large_perc_diff_dict")
            elif self.smallestPerc.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "TS_small_perc_diff_dict")
                
        elif self.averageSpeedItem.GetValue() == True:
            if self.largest2Smallest.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "AS_large_dict")
            elif self.smallest2Largest.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "AS_small_dict")
            elif self.largestDiff.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "AS_large_diff_dict")
            elif self.smallestDiff.GetValue() == True:
                wx.CallAfter(pub.sendMessage,"SortType", "AS_small_diff_dict")
            elif self.largestPerc.GetValue() == True:
                wx.CallAfter(pub.sendMessage,"SortType", "AS_large_perc_diff_dict")
            elif self.smallestPerc.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "AS_small_perc_diff_dict")
                
        elif self.topPowerItem.GetValue() == True:
            if self.largest2Smallest.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "TP_large_dict")
            elif self.smallest2Largest.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "TP_small_dict")
            elif self.largestDiff.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "TP_large_diff_dict")
            elif self.smallestDiff.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "TP_small_diff_dict")
            elif self.largestPerc.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "TP_large_perc_diff_dict")
            elif self.smallestPerc.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "TP_small_perc_diff_dict")
                
        elif self.averagePowerItem.GetValue() == True:
            if self.largest2Smallest.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "AP_large_dict")
            elif self.smallest2Largest.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "AP_small_dict")
            elif self.largestDiff.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "AP_large_diff_dict")
            elif self.smallestDiff.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "AP_small_diff_dict")
            elif self.largestPerc.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "AP_large_perc_diff_dict")
            elif self.smallestPerc.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "AP_small_perc_diff_dict")
                
        elif self.energyItem.GetValue() == True:
            if self.largest2Smallest.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "E_large_dict")
            elif self.smallest2Largest.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "E_small_dict")
            elif self.largestDiff.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "E_large_diff_dict")
            elif self.smallestDiff.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "E_small_diff_dict")
            elif self.largestPerc.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "E_large_perc_diff_dict")
            elif self.smallestPerc.GetValue() == True:
                wx.CallAfter(pub.sendMessage, "SortType", "E_small_perc_diff_dict")
                
        else:
            pass
            
class SAResultsPanel(wx.Panel):
    """Right panel in WIP GUI window that shows all the results after running the simulation"""
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent  

        self.sortArrays = collections.OrderedDict()
        self.completeResults = collections.OrderedDict()
        self.directory = ''
        self.sensitivityValue = 0       
        self.cellBlockSize = 0
        self.inputValues = dict()
        
        
        pub.subscribe(self.TransferSortArrays, ("TransferSortArrays"))
        pub.subscribe(self.TransferDictionary, ("TransferSADictionary"))
        pub.subscribe(self.TransferOutputDirectory, ("TransferOutputDirectory"))
        pub.subscribe(self.TransferSensitivityValue, ("TransferSensitivityValue"))
        pub.subscribe(self.InsertPages, ("TransferSADictionary")) 
        pub.subscribe(self.UpdateNotebook, ("DisplayOutputs"))
        pub.subscribe(self.DetermineSortType, ("SortType"))
        pub.subscribe(self.ObtainInputs, ("GetInputs"))
        
        self.lowerSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lowerSizer.AddSpacer(50)
        
        self.saveDetailed = wx.CheckBox(self, wx.ID_ANY, "Save detailed simulation results")
        self.saveSummary = wx.CheckBox(self, wx.ID_ANY, "Save sensitivity analysis summaries")
        self.saveButton = wx.Button(self, wx.ID_ANY, "Save Sensitivity Analysis")
        
        
        self.lowerSizer.Add(self.saveDetailed, 1, wx.ALL | wx.EXPAND)
        self.lowerSizer.AddSpacer(50)
        self.lowerSizer.Add(self.saveSummary, 1, wx.ALL | wx.EXPAND)
        self.lowerSizer.AddSpacer(50)
        self.lowerSizer.Add(self.saveButton, 1, wx.CENTER)
        self.lowerSizer.AddSpacer(10)
        
        self.Bind(wx.EVT_BUTTON, self.SaveSA, self.saveButton)
        # Default sort type
        self.sortType = 'TS_large_dict'
        
        self.pages = []
        self.outputs = []
        self.SADict = collections.OrderedDict()
        self.notebook = wx.Notebook(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.ALL | wx.EXPAND)
        self.lowerSizer.Layout()
        sizer.Add(self.lowerSizer)
        
        self.SetSizer(sizer)               
        
        
        #self.notebook.Bind(wx.EVT_MOTION, self.onMouseMove)        
        
        self.Layout()
        self.SetAutoLayout(1)

    def TransferDictionary(self, msg):
        self.completeResults = msg.data   

    def TransferSortArrays(self, msg):
        self.sortArrays = msg.data

    def TransferOutputDirectory(self, msg):
        self.directory = msg.data
        
    def TransferSensitivityValue(self,msg):
        self.sensitivityValue = msg.data
        print self.sensitivityValue

    def DetermineSortType(self, msg):
        self.sortType = msg.data
        self.RegeneratePages()
    
    def UpdateNotebook(self, msg):
        self.outputs = msg.data
        self.RegeneratePages()

    def ObtainInputs(self, msg):
        self.inputValues = msg.data
    
    def RegeneratePages(self):
        pageNum = 0
        
        self.notebook.GetSize()
        for page in self.pages:
            page.myGrid.ClearGrid()
            tabName = self.notebook.GetPageText(pageNum)
            self.CreateOutputGrid(page, tabName, self.sortArrays[self.sortType][tabName])
            pageNum += 1    

        
    def InsertPages(self, msg):
        self.SADict = msg.data
        self.parent.Show()
        self.GrandParent.Show()
        for file in self.SADict['gearing'][0]: 
            self.page = NewTabPanel(self.notebook)
            self.pages.append(self.page)
            self.page.myGrid.CreateGrid(450,30)
            self.page.myGrid.HideColLabels()
            self.page.myGrid.HideRowLabels()
            self.page.myGrid.EnableGridLines(False)
            #sortedArray = self.sortArrays[self.sortType][file]
            #print sortedArray
            #self.CreateOutputGrid(self.page, file, sortedArray)
            self.notebook.AddPage(self.page, file)            
        
        self.page.Update()
        
    def CreateOutputGrid(self, page, file, sortedArray):   
        
        #self.page.myGrid.SetCellHighlightColour(self,'#14FF63' )
        currentBlocksInRow = 0
        row = 0
        col = 0
        for parameter in sortedArray:
            if parameter[1] in self.outputs:
                currentBlocksInRow += 1
                #print "Current page for parameter " + parameter[1] + " is " + file
                parameter = parameter[1]
                
                # Row 0, Col 0 or 8
                page.myGrid.SetCellValue(row, col, parameter)
                page.myGrid.SetCellValue(row, col+1, "Input Value")
                page.myGrid.SetCellValue(row, col+2, str(self.inputValues[file][parameter][0]))
                page.myGrid.SetCellFont(row, col, wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD))
    
                # Row 1, Col 0 or 8
                #self.parameterSizer.AddSpacer(0)
                #self.parameterSizer.Add(plusStaticText)
                page.myGrid.SetCellValue(row+1, col+1, "+" + str(self.sensitivityValue) + "%")
                #self.parameterSizer.Add(negativeStaticText)
                page.myGrid.SetCellValue(row+1, col+2, "-" + str(self.sensitivityValue) + "%")
                #self.parameterSizer.Add(diffStaticText)
                page.myGrid.SetCellValue(row+1, col+3, "Diff")
                #self.parameterSizer.Add(pdStaticText)
                page.myGrid.SetCellValue(row+1, col+4, "% Diff")

                # Row 2, Col 0 or 8
                page.myGrid.SetCellBackgroundColour(row+2, col+1, '#FFFFFF')
                page.myGrid.SetCellBackgroundColour(row+2, col+2, '#FFFFFF')
                page.myGrid.SetCellBackgroundColour(row+2, col+3, '#FFFFFF')
                page.myGrid.SetCellBackgroundColour(row+2, col+4, '#FFFFFF')
                if self.sortType == 'TS_large_dict':
                    page.myGrid.SetCellBackgroundColour(row+2, col+1, '#14FF63')
                    #print 'I changed cell background for file: ' + file
                elif self.sortType == 'TS_small_dict':
                    page.myGrid.SetCellBackgroundColour(row+2, col+2, '#14FF63')
                elif self.sortType == 'TS_large_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+2, col+3, '#14FF63')
                elif self.sortType == 'TS_small_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+2, col+3, '#14FF63')
                elif self.sortType == 'TS_large_perc_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+2, col+4, '#14FF63')
                elif self.sortType == 'TS_small_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+2, col+4, '#14FF63')
                    
                page.myGrid.SetCellValue(row+2, col, "Max MPH")
                plusValue = self.SADict[parameter][0][file]['Max MPH']
                page.myGrid.SetCellValue(row+2, col+1, repr(round(plusValue,2)))
                minusValue = self.SADict[parameter][1][file]['Max MPH']
                page.myGrid.SetCellValue(row+2, col+2, repr(round(minusValue,2)))
                diff = abs(plusValue - minusValue)
                page.myGrid.SetCellValue(row+2, col+3, repr(round(diff,2)))
                if (plusValue+minusValue) == 0:
                    percentDiff = 0
                else:
                    percentDiff = diff/(plusValue + minusValue) * 100
                page.myGrid.SetCellValue(row+2, col+4, repr(round(percentDiff,2)))
                
                
                # Row 3, Col 0 or 8
                page.myGrid.SetCellBackgroundColour(row+3, col+1, '#FFFFFF')
                page.myGrid.SetCellBackgroundColour(row+3, col+2, '#FFFFFF')
                page.myGrid.SetCellBackgroundColour(row+3, col+3, '#FFFFFF')
                page.myGrid.SetCellBackgroundColour(row+3, col+4, '#FFFFFF')
                if self.sortType == 'AS_large_dict':
                    page.myGrid.SetCellBackgroundColour(row+3, col+1, '#14FF63')
                elif self.sortType == 'AS_small_dict':
                    page.myGrid.SetCellBackgroundColour(row+3, col+2, '#14FF63')
                elif self.sortType == 'AS_large_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+3, col+3, '#14FF63')
                elif self.sortType == 'AS_small_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+3, col+3, '#14FF63')
                elif self.sortType == 'AS_large_perc_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+3, col+4, '#14FF63')
                elif self.sortType == 'AS_small_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+3, col+4, '#14FF63')
                    
                page.myGrid.SetCellValue(row+3, col, "Average MPH")
                plusValue = self.SADict[parameter][0][file]['Average MPH']
                page.myGrid.SetCellValue(row+3, col+1, repr(round(plusValue,2)))
                minusValue = self.SADict[parameter][1][file]['Average MPH']
                page.myGrid.SetCellValue(row+3, col+2, repr(round(minusValue,2)))
                diff = abs(plusValue - minusValue)
                page.myGrid.SetCellValue(row+3, col+3, repr(round(diff,2)))
                if (plusValue+minusValue) == 0:
                    percentDiff = 0
                else:
                    percentDiff = diff/(plusValue + minusValue) * 100
                page.myGrid.SetCellValue(row+3, col+4, repr(round(percentDiff,2)))
                
                
                # Row 4, Col 0 or 8
                page.myGrid.SetCellBackgroundColour(row+4, col+1, '#FFFFFF')
                page.myGrid.SetCellBackgroundColour(row+4, col+2, '#FFFFFF')
                page.myGrid.SetCellBackgroundColour(row+4, col+3, '#FFFFFF')
                page.myGrid.SetCellBackgroundColour(row+4, col+4, '#FFFFFF')
                if self.sortType == 'TP_large_dict':
                    page.myGrid.SetCellBackgroundColour(row+4, col+1, '#14FF63')
                elif self.sortType == 'TP_small_dict':
                    page.myGrid.SetCellBackgroundColour(row+4, col+2, '#14FF63')
                elif self.sortType == 'TP_large_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+4, col+3, '#14FF63')
                elif self.sortType == 'TP_small_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+4, col+3, '#14FF63')
                elif self.sortType == 'TP_large_perc_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+4, col+4, '#14FF63')
                elif self.sortType == 'TP_small_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+4, col+4, '#14FF63')
                    
                page.myGrid.SetCellValue(row+4, col, "Max Power")
                plusValue = self.SADict[parameter][0][file]['Max Power (Watts)']
                page.myGrid.SetCellValue(row+4, col+1, repr(round(plusValue,2)))
                minusValue = self.SADict[parameter][1][file]['Max Power (Watts)']
                page.myGrid.SetCellValue(row+4, col+2, repr(round(minusValue,2)))
                diff = abs(plusValue - minusValue)
                page.myGrid.SetCellValue(row+4, col+3, repr(round(diff,2)))
                if (plusValue+minusValue) == 0:
                    percentDiff = 0
                else:
                    percentDiff = diff/(plusValue + minusValue) * 100
                page.myGrid.SetCellValue(row+4, col+4, repr(round(percentDiff,2)))
    
                # Row 5, Col 0 or 8
                page.myGrid.SetCellBackgroundColour(row+5, col+1, '#FFFFFF')
                page.myGrid.SetCellBackgroundColour(row+5, col+2, '#FFFFFF')
                page.myGrid.SetCellBackgroundColour(row+5, col+3, '#FFFFFF')
                page.myGrid.SetCellBackgroundColour(row+5, col+4, '#FFFFFF')
                if self.sortType == 'AP_large_dict':
                    page.myGrid.SetCellBackgroundColour(row+5, col+1, '#14FF63')
                elif self.sortType == 'AP_small_dict':
                    page.myGrid.SetCellBackgroundColour(row+5, col+2, '#14FF63')
                elif self.sortType == 'AP_large_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+5, col+3, '#14FF63')
                elif self.sortType == 'AP_small_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+5, col+3, '#14FF63')
                elif self.sortType == 'AP_large_perc_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+5, col+4, '#14FF63')
                elif self.sortType == 'AP_small_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+5, col+4, '#14FF63')
                    
                page.myGrid.SetCellValue(row+5, col, "Average Power")
                plusValue = self.SADict[parameter][0][file]['Average Power (Watts)']
                page.myGrid.SetCellValue(row+5, col+1, repr(round(plusValue,2)))
                minusValue = self.SADict[parameter][1][file]['Average Power (Watts)']
                page.myGrid.SetCellValue(row+5, col+2, repr(round(minusValue,2)))
                diff = abs(plusValue - minusValue)
                page.myGrid.SetCellValue(row+5, col+3, repr(round(diff,2)))
                if (plusValue+minusValue) == 0:
                    percentDiff = 0
                else:
                    percentDiff = diff/(plusValue + minusValue) * 100
                page.myGrid.SetCellValue(row+5, col+4, repr(round(percentDiff,2)))
                        
                # Row 6, Col 0 or 8
                page.myGrid.SetCellBackgroundColour(row+6, col+1, '#FFFFFF')
                page.myGrid.SetCellBackgroundColour(row+6, col+2, '#FFFFFF')
                page.myGrid.SetCellBackgroundColour(row+6, col+3, '#FFFFFF')
                page.myGrid.SetCellBackgroundColour(row+6, col+4, '#FFFFFF')
                if self.sortType == 'E_large_dict':
                    page.myGrid.SetCellBackgroundColour(row+6, col+1, '#14FF63')
                elif self.sortType == 'E_small_dict':
                    page.myGrid.SetCellBackgroundColour(row+6, col+2, '#14FF63')
                elif self.sortType == 'E_large_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+6, col+3, '#14FF63')
                elif self.sortType == 'E_small_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+6, col+3, '#14FF63')
                elif self.sortType == 'E_large_perc_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+6, col+4, '#14FF63')
                elif self.sortType == 'E_small_diff_dict':
                    page.myGrid.SetCellBackgroundColour(row+6, col+4, '#14FF63')
                    
                page.myGrid.SetCellValue(row+6, col, "Max Energy")
                plusValue = self.SADict[parameter][0][file]['Max Energy (Wh)']
                page.myGrid.SetCellValue(row+6, col+1, repr(round(plusValue,2)))
                minusValue = self.SADict[parameter][1][file]['Max Energy (Wh)']
                page.myGrid.SetCellValue(row+6, col+2, repr(round(minusValue,2)))
                diff = abs(plusValue - minusValue)
                page.myGrid.SetCellValue(row+6, col+3, repr(round(diff,2)))
                if (plusValue+minusValue) == 0:
                    percentDiff = 0
                else:
                    percentDiff = diff/(plusValue + minusValue) * 100
                page.myGrid.SetCellValue(row+6, col+4, repr(round(percentDiff,2)))
                
                # Row 8, Col 0 or 8
                # % Motor RPM Limit
                page.myGrid.SetCellValue(row+8, col, "% Motor RPM Limit")
                plus_limit = self.SADict[parameter][0][file]['% Motor RPM Limit']
                minus_limit = self.SADict[parameter][1][file]['% Motor RPM Limit']
                page.myGrid.SetCellValue(row+8, col+1, repr(round(plus_limit,2)))
                page.myGrid.SetCellValue(row+8, col+2, repr(round(minus_limit,2)))
                diff = abs(plus_limit - minus_limit)
                page.myGrid.SetCellValue(row+8, col+3, repr(round(diff,2)))
                if (plusValue+minusValue) == 0:
                    percentDiff = 0
                else:
                    percentDiff = diff/(plusValue + minusValue) * 100
                page.myGrid.SetCellValue(row+8, col+4, repr(round(percentDiff,2)))
                
                # Row 8, Col 0 or 8
                # % Motor Torque Limit
                page.myGrid.SetCellValue(row+9, col, "% Motor Torque Limit")
                plus_limit = self.SADict[parameter][0][file]['% Motor Torque Limit']
                minus_limit = self.SADict[parameter][1][file]['% Motor Torque Limit']
                page.myGrid.SetCellValue(row+9, col+1, repr(round(plus_limit,2)))
                page.myGrid.SetCellValue(row+9, col+2, repr(round(minus_limit,2)))
                diff = abs(plus_limit - minus_limit)
                page.myGrid.SetCellValue(row+9, col+3, repr(round(diff,2)))
                if (plusValue+minusValue) == 0:
                    percentDiff = 0
                else:
                    percentDiff = diff/(plusValue + minusValue) * 100
                page.myGrid.SetCellValue(row+9, col+4, repr(round(percentDiff,2)))
                
                # Row 9, Col 0 or 8
                # % Motor Power Limit
                page.myGrid.SetCellValue(row+10, col, "% Motor Power Limit")
                plus_limit = self.SADict[parameter][0][file]['% Motor Power Limit']
                minus_limit = self.SADict[parameter][1][file]['% Motor Power Limit']
                page.myGrid.SetCellValue(row+10, col+1, repr(round(plus_limit,2)))
                page.myGrid.SetCellValue(row+10, col+2, repr(round(minus_limit,2)))
                diff = abs(plus_limit - minus_limit)
                page.myGrid.SetCellValue(row+10, col+3, repr(round(diff,2)))
                if (plusValue+minusValue) == 0:
                    percentDiff = 0
                else:
                    percentDiff = diff/(plusValue + minusValue) * 100
                page.myGrid.SetCellValue(row+10, col+4, repr(round(percentDiff,2)))
                
                # Row 10, Col 0 or 8
                # % Battery Power Limit
                page.myGrid.SetCellValue(row+11, col, "% Battery Power Limit")
                plus_limit = self.SADict[parameter][0][file]['% Battery Power Limit']
                minus_limit = self.SADict[parameter][1][file]['% Battery Power Limit']
                page.myGrid.SetCellValue(row+11, col+1, repr(round(plus_limit,2)))
                page.myGrid.SetCellValue(row+11, col+2, repr(round(minus_limit,2)))
                diff = abs(plus_limit - minus_limit)
                page.myGrid.SetCellValue(row+11, col+3, repr(round(diff,2)))
                if (plusValue+minusValue) == 0:
                    percentDiff = 0
                else:
                    percentDiff = diff/(plusValue + minusValue) * 100
                page.myGrid.SetCellValue(row+11, col+4, repr(round(percentDiff,2)))
                
                # Row 11, Col 0 or 8
                # % Motor Thermal Limit
                page.myGrid.SetCellValue(row+12, col, "% Motor Thermal Limit")
                plus_limit = self.SADict[parameter][0][file]['% Motor Thermal Limit']
                minus_limit = self.SADict[parameter][1][file]['% Motor Thermal Limit']
                page.myGrid.SetCellValue(row+12, col+1, repr(round(plus_limit,2)))
                page.myGrid.SetCellValue(row+12, col+2, repr(round(minus_limit,2)))
                diff = abs(plus_limit - minus_limit)
                page.myGrid.SetCellValue(row+12, col+3, repr(round(diff,2)))
                if (plusValue+minusValue) == 0:
                    percentDiff = 0
                else:
                    percentDiff = diff/(plusValue + minusValue) * 100
                page.myGrid.SetCellValue(row+12, col+4, repr(round(percentDiff,2)))
                
                # Row 12, Col 0 or 8
                # % Lean Angle Limit
                page.myGrid.SetCellValue(row+13, col, "% Lean Angle Limit")
                plus_limit = self.SADict[parameter][0][file]['% Lean Angle Limit']
                minus_limit = self.SADict[parameter][1][file]['% Lean Angle Limit']
                page.myGrid.SetCellValue(row+13, col+1, repr(round(plus_limit,2)))
                page.myGrid.SetCellValue(row+13, col+2, repr(round(minus_limit,2)))
                diff = abs(plus_limit - minus_limit)
                page.myGrid.SetCellValue(row+13, col+3, repr(round(diff,2)))
                if (plusValue+minusValue) == 0:
                    percentDiff = 0
                else:
                    percentDiff = diff/(plusValue + minusValue) * 100
                page.myGrid.SetCellValue(row+13, col+4, repr(round(percentDiff,2)))
                
                ''' If we haven't obtained the cell block size yet, resize the columns
                after the first block is generated and then count the cells widths '''
                if self.cellBlockSize == 0:
                    page.myGrid.AutoSizeColumns()
                    cellCountingCol = 0
                    while cellCountingCol < 6:
                        self.cellBlockSize += page.myGrid.GetColSize(cellCountingCol)
                        cellCountingCol += 1
                
                if ((self.cellBlockSize) * (currentBlocksInRow+1)) < self.GetSize()[0]:
                    col += 6
                else:
                    currentBlocksInRow = 0
                    col = 0
                    row += 15
                    

        page.myGrid.AutoSizeColumns()
        #page.myGrid.ForceRefresh()
    
    def SaveSA(self, e):

        #print parameterDict[parameterDict.keys()[0]][0]['TestTemplateOutput.csv']['Max MPH']
        if not os.path.exists(self.directory + '\Sensitivity Analysis'):
            os.makedirs(self.directory + '\Sensitivity Analysis')
        outputDict = collections.OrderedDict()
        
        if self.saveDetailed.GetValue() == 1:
            for parameter in self.completeResults.keys():
                for file in self.completeResults[parameter][0].keys():
                    #outputFile = "Gearing_15up_originalFileName"
                    # Plus x% files
                    outputFile = parameter + "_15plus" + file
                    outputDict[outputFile] = self.completeResults[parameter][0][file]
                    # Minus x% files
                    outputFile = parameter + "_15minus" + file
                    outputDict[outputFile] = self.completeResults[parameter][1][file]
                    
            # Save to the Sensitivity Analysis folder in the output folder
            OutputFile(self.directory + '\Sensitivity Analysis', outputDict)
        #self.completeResults
        #Obtain each tab
        if self.saveSummary.GetValue() == 1:
            pageNum = 0
            for page in self.pages:
                fileName = self.directory + "\Sensitivity Analysis\SA_summary_" + self.notebook.GetPageText(pageNum)
                data = np.zeros((page.myGrid.GetNumberRows(),page.myGrid.GetNumberCols()), dtype = '|S50')
                row = 0
                while row < page.myGrid.GetNumberRows():
                    col = 0
                    while col < page.myGrid.GetNumberCols():
                        data[row,col] = page.myGrid.GetCellValue(row, col)
                        col += 1
                    row += 1    
                try:
                    np.savetxt(fileName, data, delimiter=",", fmt="%s")
                except IOError:
                    logging.critical("Unable to save %s",fileName)
                    GUIdialog = wx.MessageDialog(None, "Unable to save file to " + fileName +". Make sure "+ fileName + " is closed, specify a new file to save to, or pick a save directory that's writable.", "Error", wx.OK)
                    GUIdialog.ShowModal()
                    GUIdialog.Destroy()            
                    raise Exception("Unable to save file")
                
                pageNum += 1
                
            logging.info("Data converted and saved to %s", fileName)



class MainFrame(wx.Frame):
    """Constructor"""
    #----------------------------------------------------------------------
    def __init__(self, parent, id):
        wx.Frame.__init__(self, None, title="SIMBA",size=(1000,1000))
        
        pub.subscribe(self.FindCurrentParamFile, ("CurrentFile")) 
        pub.subscribe(self.SetDictionary, ("DictFromInput"))
        pub.subscribe(self.SetCurrentFiles, ("InputFiles"))
        pub.subscribe(self.ChangeProjectName, ("ProjectName"))        
        pub.subscribe(self.DisableDeleteCopy, ("DisableDelete"))        
        pub.subscribe(self.CopyFileToFile, ("InputFile"))
                
        self.fileToFile = dict()
        self.currentFiles = np.empty(shape=(0,0))
        self.currentFile = dict()   
        self.performSensitivityAnalysis = False
        # Load icon
        if hasattr(sys, 'frozen'):
            iconLoc = os.path.join(os.path.dirname(sys.executable),"SIMBA.exe")
            iconLoc = wx.IconLocation(iconLoc,0)
            self.SetIcon(wx.IconFromLocation(iconLoc))
        #else:
         #   iconLoc = os.path.join(os.path.dirname(__file__),__file__)

        # Setting up toolbar
        self.toolbar = self.CreateToolBar()
        #self.toolbar2 = self.CreateToolBar()
        self.toolbar.SetToolBitmapSize((20,20))  # sets icon size
        
        newProject_ico = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE)  
        newProjectTool = self.toolbar.AddSimpleTool(wx.ID_NEW, newProject_ico, "New Project", "Create a new project")
        self.Bind(wx.EVT_MENU, self.OnNewProject, newProjectTool)    
        #self.toolbar.EnableTool(wx.ID_NEW, False)
        
        openProject_ico = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (20,20))
        openProjectTool = self.toolbar.AddSimpleTool(wx.ID_ANY, openProject_ico, "Open Project", "Open a past project")
        self.Bind(wx.EVT_MENU, self.OnOpen, openProjectTool)        
        
        save_ico = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, (20,20))
        saveTool = self.toolbar.AddSimpleTool(wx.ID_ANY, save_ico, "Save", "Saves the current parameter file")
        self.Bind(wx.EVT_MENU, self.OnSave, saveTool)
 
        save_all_ico = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_TOOLBAR, (20,20))
        saveAllTool = self.toolbar.AddSimpleTool(wx.ID_ANY, save_all_ico, "Save All Files", "Saves all parameters files")
        self.Bind(wx.EVT_MENU, self.OnSaveAll, saveAllTool)
        
        self.toolbar.AddSeparator()

        self.newParamName = wx.TextCtrl(self.toolbar, size = (200, -1))   
        self.toolbar.AddControl(wx.StaticText(self.toolbar, wx.ID_ANY, " Parameter Filename  "))
        self.toolbar.AddControl(self.newParamName)
        
        addParamFile_ico = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, (20,20))
        addNewParamTool = self.toolbar.AddSimpleTool(wx.ID_FILE, addParamFile_ico, "New Parameter File", "Add new paramter file to project")
        self.Bind(wx.EVT_MENU, self.OnNewParamFile, addNewParamTool)
        
        copyParamFile_ico = wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_TOOLBAR, (20,20))
        copyParamTool = self.toolbar.AddSimpleTool(wx.ID_COPY, copyParamFile_ico, "Copy Parameter File", "Copy the current parameter file to a new parameter file")
        self.Bind(wx.EVT_MENU, self.OnCopyParamFile, copyParamTool)
        self.toolbar.EnableTool(wx.ID_COPY, False)
        
        importParamFile_ico = wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE, wx.ART_TOOLBAR, (20,20))
        importParamTool = self.toolbar.AddSimpleTool(wx.ID_FILE2, importParamFile_ico, "Import Parameter File", "Import a parameter file into the project")
        self.Bind(wx.EVT_MENU, self.OnImportParamFile, importParamTool)        
        
        removeParamFile_ico = wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR, (20,20))
        removeNewParamTool = self.toolbar.AddSimpleTool(wx.ID_DELETE, removeParamFile_ico, "Remove Parameter File", "Remove parameter file from project")
        self.Bind(wx.EVT_MENU, self.OnRemoveParamFile, removeNewParamTool)
        self.toolbar.EnableTool(wx.ID_DELETE, False)
        
        run_ico = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR, (20,20))
        runTool = self.toolbar.AddSimpleTool(wx.ID_ANY, run_ico, "Run Simulation", "Runs the simulation with the opened project")
        self.Bind(wx.EVT_MENU, self.OnRun, runTool)
        
        self.toolbar.AddSeparator()
        
        #self.toolbar.AddControl(TransparentText(self.toolbar, wx.ID_ANY, " Output Directory  "))
        self.textTest = wx.StaticText(self.toolbar, wx.ID_ANY, " Output Directory  ")
        self.toolbar.AddControl(self.textTest)
        #self.textTest.SetBackgroundColour(wx.TRANSPARENT)
        self.folderControl = wx.TextCtrl(self.toolbar, size = (300,-1))
        self.toolbar.AddControl(self.folderControl) 
        self.toolbar.AddControl(wx.StaticText(self.toolbar, wx.ID_ANY, "  "))
        self.toolbar.AddSeparator()        
        
        self.sensitivityCheckbox = wx.CheckBox(self.toolbar, wx.ID_ANY, label = "Perform sensitivity analysis  ")
        self.toolbar.AddControl(self.sensitivityCheckbox)
        
        self.toolbar.AddSeparator()
        self.toolbar.AddControl(wx.StaticText(self.toolbar, wx.ID_ANY, " Sensitivity Adjustment Value: "))
        self.sensitivityControl = mask.NumCtrl(self.toolbar, wx.ID_ANY, integerWidth = 2, allowNegative = False)
        self.toolbar.AddControl(self.sensitivityControl)
        self.toolbar.AddControl(wx.StaticText(self.toolbar, wx.ID_ANY, " %"))        
        
        # Setting up menu
        filemenu = wx.Menu()
        self.menuNewFile = filemenu.Append(wx.ID_NEW, "New Parameter File", "Create a new parameter file for the current project")
        self.menuNewProject = filemenu.Append(wx.ID_ANY, "New Project", "Create a new project")
        self.menuNewProject.Enable(False)
        self.menuOpenProject = filemenu.Append(wx.ID_OPEN, "Open Project", "Open a project")
        self.menuSave = filemenu.Append(wx.ID_SAVE, "Save File", "Save a parameter file")
        self.menuSaveAll = filemenu.Append(wx.ID_ANY, "Save All", "Save all parameter files")
        self.menuSaveProject = filemenu.Append(wx.ID_ANY, "Save Project", "Save project with all parameter files")
        self.menuSaveProject.Enable(False)
        self.menuExit = filemenu.Append(wx.ID_EXIT, "&Exit"," Terminate the program")
        
        runmenu = wx.Menu()
        self.menuRun = runmenu.Append(wx.ID_ANY, "Run simulation", "Runs the simulation with the opened project")
        
        aboutmenu = wx.Menu()
        self.menuAbout = aboutmenu.Append(wx.ID_ABOUT, "About"," Information about this program")

        
        # Creating menubar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File") #Adds "filemenu" to the MenuBar
        menuBar.Append(runmenu, "&Run")
        menuBar.Append(aboutmenu, "&About")
        
        self.SetMenuBar(menuBar)        
        
        
        # Setting events
        self.Bind(wx.EVT_MENU, self.OnAbout, self.menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, self.menuExit)
        self.Bind(wx.EVT_MENU, self.OnNewProject, self.menuNewProject)
#        self.Bind(wx.EVT_MENU, self.OnNewFile, self.menuNewFile)
        self.Bind(wx.EVT_MENU, self.OnSaveAll, self.menuSaveAll)
        self.Bind(wx.EVT_CHECKBOX, self.SA_Checkbox_Event, self.sensitivityCheckbox)  
        
        #self.Bind(wx.EVT_MENU_HIGHLIGHT_ALL, self.resetStatusBar) 
        
        ################################################################
        # Define mainsplitter as child of Frame and add IOSplitterPanel and StatusPanel as children
        mainsplitter = wx.SplitterWindow(self, style = wx.SP_3D| wx.SP_LIVE_UPDATE)
        mainsplitter.SetSashGravity(0.005)
        #mainsplitter.SetSashPosition(20)
        mainsplitter.SetMinimumPaneSize(20)

        splitterpanel = IOSplitterPanel(mainsplitter)
        #statusPanel = StatusPanel(mainsplitter, style = wx.BORDER_SIMPLE)

        leftPanel = InputPanel(mainsplitter, style = wx.BORDER_SIMPLE | wx.TAB_TRAVERSAL)
        mainsplitter.SplitVertically(leftPanel, splitterpanel)
        windowW, windowH = wx.DisplaySize()
        newH = windowH/1.7
        mainsplitter.SetSashPosition(windowH - newH, True)
        MainSizer = wx.BoxSizer(wx.VERTICAL)
        MainSizer.Add(mainsplitter, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(MainSizer)
        #################################################################
        self.toolbar.Realize()
        self.Refresh()
        self.Show()
        self.Maximize(True)
        
        self.dictionary = dict()
        self.project = ""
        self.dirname = ""


    def ChangeProjectName(self, msg):
        
        if not msg.data == "Cancel":
            if hasattr(sys, 'frozen'):
                test_in = os.path.join(os.path.dirname(sys.executable),"test_in")
            else:
                test_in = os.path.normpath("C:/Users/Sean/Desktop/Buckeye Current/Simulation Local/Deployment Package/test_in/")
            newDirectory = os.path.join(test_in, msg.data)
            
            if not os.path.exists(newDirectory):
                os.makedirs(newDirectory)
            
            self.project = os.path.join(newDirectory, "OPTIONS.csv")
            self.dictionary = dict()
            projectArray = np.array(["Files In", "Files Out", "Comments", "Output Folder", "Final Report Title"])
            np.savetxt(self.project, projectArray.reshape(1, projectArray.shape[0]), delimiter=",", fmt="%s")
            
            wx.CallAfter(pub.sendMessage, "UpdateInput", self.dictionary)
            
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Successfully created new project: " + newDirectory
            wx.CallAfter(pub.sendMessage, "AddStatus", msg)    
        

    def DisableDeleteCopy(self, msg):
        
        if msg.data == True:
            self.toolbar.EnableTool(wx.ID_DELETE, False)
            self.toolbar.EnableTool(wx.ID_COPY, False)
        else:
            self.toolbar.EnableTool(wx.ID_DELETE, True)
            self.toolbar.EnableTool(wx.ID_COPY, True)
    
    def FindCurrentParamFile(self, msg):
        self.currentFile = msg.data
        
        
    def SetDictionary(self, msg):
        self.dictionary = msg.data
        wx.CallAfter(pub.sendMessage, "UpdateInput", self.dictionary)
        
    def SetCurrentFiles(self, msg):
        self.currentFiles = msg.data
        
    def OnNewProject(self,e):
        #Ask user if they want to save current project
        dlg = wx.MessageDialog(self, "Do you want to save the current project before creating a new one?", style = wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            #Simply saves the current open project as it's current name
            if not self.project == "":
                self.OnSaveAll(wx.EVT_ACTIVATE)
            
            # Allows the user to save current project as any name.
            '''
            savedlg = wx.FileDialog(self, "Save project", "", "", ".csv|*.csv", style = wx.FD_SAVE)
            if savedlg.ShowModal() == wx.ID_OK:
                self.filename = savedlg.GetFilename()
                self.dirname = savedlg.GetDirectory()
                outputFolder = self.folderControl.GetValue()
                oldProject = os.path.join(self.dirname, self.filename)
                inFiles = np.array(["Files In", "Files Out", "Comment", "OutputFolder", "Final Report Title"], ['','','','',''])
                for item in self.currentFiles:    
                    newline = np.array([item, item, self.dictionary[item]["comments"][0], '', ''], dtype = "|S50")
                    inFiles = np.vstack((inFiles, newline))
                
                inFiles[1,3] = outputFolder
                inFiles[1,4] = 'Simulation Report'
                np.savetxt(oldProject, inFiles, delimiter=",", fmt="%s")
            #OutputFile(self.optionsControl.GetValue(), self.dictionary)
            '''
            
        frame = PopupFrame()
        frame.Show()    
        
    
    def OnOpen(self,e):
        
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "Comma Seperated Value (.csv)|*.csv|Text file (.txt)|*.txt")
        if dlg.ShowModal() == wx.ID_OK:
            
            wx.CallAfter(pub.sendMessage, "RemoveFiles", True)
            hasParamFile = False
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.project = (os.path.join(self.dirname, self.filename))
            
            if os.path.exists(self.project):
                try:
                    data = np.loadtxt(open(self.project, "rb"), dtype = 'string', delimiter=',')
                    
                    if not np.shape(data) == (5,):
                        hasParamFile = True
                        fileIndex = 1
                        while fileIndex < np.shape(data)[1]:

                            fileIndex = fileIndex+1
                            
                    if self.folderControl.IsEmpty():
                        self.folderControl.SetValue(data[1,3])
                    
                #Extracts all data from file into variable data
                except:
                    print "failed opening file"
            
          
            if hasParamFile:
                self.dictionary = ProjectToParams(self.project)

            else:
                self.dictionary.clear()
                msg = datetime.now().strftime('%H:%M:%S') + ": " + self.project + " has no parameter files"
                wx.CallAfter(pub.sendMessage, "AddStatus", msg)  
                
            wx.CallAfter(pub.sendMessage, "UpdateInput", self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Opened project " + self.project
            wx.CallAfter(pub.sendMessage, "AddStatus", msg)    
              
            
            
        dlg.Destroy()
          
        
    
    def OnSave(self, e):
        """Saves the current parameter file open in input panel"""
        currentFile = self.fileToFile.keys()[self.fileToFile.values().index(self.currentFile.keys()[0])]
        saveDict = dict()
        saveDict[currentFile] = self.currentFile[self.currentFile.keys()[0]]
        SaveInput(os.path.dirname(os.path.realpath(self.project)), saveDict)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Successfully saved " + saveDict.keys()[0]
        wx.CallAfter(pub.sendMessage, "AddStatus", msg)  
        
        optionsData = np.loadtxt(open(self.project, "rb"), dtype = 'string', delimiter=',')
        if np.shape(optionsData)[0] > 1:
            optionsData[np.where(self.currentFiles == saveDict.keys()[0])[0][0]+1,2] = self.dictionary[self.currentFile.keys()[0]]["comments"][0]
            np.savetxt(self.project, optionsData, delimiter=",", fmt="%s")
                
    def CopyFileToFile(self, msg):
        self.fileToFile = msg.data
        
    def OnSaveAll(self,e):
        """Saves all parameters file in the current project"""
        
        optionsData = np.loadtxt(open(self.project, "rb"), dtype = 'string', delimiter=',')
        for key in self.fileToFile.keys():
            saveDict = dict()
            saveDict[key] = self.dictionary[self.fileToFile[key]]
            SaveInput(os.path.dirname(os.path.realpath(self.project)), saveDict)

            if np.shape(optionsData)[0] > 1:
                optionsData[np.where(self.currentFiles == key)[0][0]+1,2] = self.dictionary[self.fileToFile[key]]["comments"][0]
                             
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Successfully saved " + key
            wx.CallAfter(pub.sendMessage, "AddStatus", msg)  
            
        np.savetxt(self.project, optionsData, delimiter=",", fmt="%s")
    
    def OnNewParamFile(self, e):
        #Get file name from input field
        #create new entry in dictionary with that name
        newParamName = self.newParamName.GetValue() + ".csv"
        if len(self.newParamName.GetValue()) > 0:
            
                
            inFiles = np.loadtxt(open(self.project, "rb"), dtype = 'string', delimiter = ',')
            if not self.newParamName.GetValue() in inFiles:        
                files = inFiles
                newline = np.array([self.newParamName.GetValue(), self.newParamName.GetValue(), '', '', ''])
                newProject = np.vstack((files, newline))
                
                if np.shape(newProject)[0] > 1:
                    newProject[1,3] = self.folderControl.GetValue()
                    newProject[1,4] = "Simulation Report.csv"
            
                np.savetxt(self.project, newProject, delimiter=",", fmt="%s")
                
             
            self.dictionary[self.newParamName.GetValue()] = collections.OrderedDict()
            self.dictionary[self.newParamName.GetValue()]["gearing"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["dist_to_alt_lookup"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["step"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["total_time"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["top_lean_angle"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["rolling_resistance"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["rider_mass"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["bike_mass"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["dist_to_speed_lookup"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["air_resistance"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["gravity"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["frontal_area"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["top_motor_current"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["top_rpm"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["max_distance_travel"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["battery_efficiency"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["motor_torque_constant"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["motor_rpm_constant"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["motor_controller_eff_lookup"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["motor_eff_lookup"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["comments"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["motor_top_power"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["batt_max_current"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["max_amphour"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["series_cells"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["soc_to_voltage_lookup"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["motor_thermal_conductivity"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["motor_heat_capacity"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["coolant_temp"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["max_motor_temp"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["throttlemap_lookup"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["chain_efficiency_lookup"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["corner_radius_lookup"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["tyreA"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["tyreB"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["tyreC"] = np.array([""])

             
            self.currentFiles = np.append(self.currentFiles, self.newParamName.GetValue())
            wx.CallAfter(pub.sendMessage, "InputFiles", self.currentFiles)
            wx.CallAfter(pub.sendMessage, "ChangeSelection", self.newParamName.GetValue())
            wx.CallAfter(pub.sendMessage, "UpdateInput", self.dictionary)
            
            if not os.path.exists(os.path.join(self.project, self.newParamName.GetValue())):
                self.OnSave(wx.EVT_ACTIVATE)                
                
        else:
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Must enter parameter filename before creating a new file"
            wx.CallAfter(pub.sendMessage, "AddStatus", msg)  
        pass
    
    def OnCopyParamFile(self, e):
        if len(self.newParamName.GetValue()) > 0:
            
            inFiles = np.loadtxt(open(self.project, "rb"), dtype = 'string', delimiter = ',')
            if not self.currentFile.keys()[0] in inFiles:    
                print "Adding in current file"
                files = inFiles
                newline = np.array([self.currentFile.keys()[0], self.currentFile.keys()[0], '', '', ''])
                newProject = np.vstack((files, newline))
                
                if np.shape(newProject)[0] > 1:
                    newProject[1,3] = self.folderControl.GetValue()
                    newProject[1,4] = "Simulation Report"

            
                np.savetxt(self.project, newProject, delimiter=",", fmt="%s")
             
            self.dictionary[self.newParamName.GetValue()] = deepcopy(self.currentFile[self.currentFile.keys()[0]])

            self.currentFiles = np.append(self.currentFiles, self.newParamName.GetValue())
            wx.CallAfter(pub.sendMessage, "InputFiles", self.currentFiles)
            wx.CallAfter(pub.sendMessage, "ChangeSelection", self.newParamName.GetValue())
            wx.CallAfter(pub.sendMessage, "UpdateInput", self.dictionary)
             

            if not os.path.exists(os.path.join(self.project, self.newParamName.GetValue())):
                self.OnSave(wx.EVT_ACTIVATE)      
    
    def OnImportParamFile(self, e):
        dlg = wx.FileDialog(self, "Import parameter file", "", "", ".csv|*.csv", style = wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:

            
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.paramFile = (os.path.join(self.dirname, self.filename))
            
            try:
                shutil.copyfile(self.paramFile, os.path.dirname(self.project) + "\\" + self.filename)   
            except:
                pass

            
            inFiles = np.loadtxt(open(self.project, "rb"), dtype = 'string', delimiter = ',')
            if not self.paramFile in inFiles:        
                files = inFiles
                newline = np.array([self.filename, self.filename, '', '', ''])
                newProject = np.vstack((files, newline))
                
                if np.shape(newProject)[0] > 1:
                    newProject[1,3] = self.folderControl.GetValue()
                    newProject[1,4] = "Simulation Report"
                    
                np.savetxt(self.project, newProject, delimiter=",", fmt="%s")

            
            self.dictionary = ProjectToParams(self.project)
            
            self.currentFiles = np.append(self.currentFiles, self.filename)
            wx.CallAfter(pub.sendMessage, "InputFiles", self.currentFiles)
            wx.CallAfter(pub.sendMessage, "ChangeSelection", self.filename)
            wx.CallAfter(pub.sendMessage, "UpdateInput", self.dictionary)
            
            if not os.path.exists(os.path.join(self.project, self.newParamName.GetValue())):
                self.OnSave(wx.EVT_ACTIVATE)  
    
    def OnRemoveParamFile(self, e):
        
        #Remove parameter fiel from
        inFiles = np.loadtxt(open(self.project, "rb"), dtype = 'string', delimiter = ',')
        if self.currentFile.keys()[0] in inFiles[1:,0]:        
            files = inFiles[inFiles[:,0] != self.currentFile.keys()[0]]
            if np.shape(files)[0] > 1:
                files[1,3] = self.folderControl.GetValue()
                files[1,4] = "Simulation Report.csv"
            np.savetxt(self.project, files, delimiter=",", fmt="%s")        
        
        #If project has a parameter file remove the opened param file in the input panel from the dict\
        newDict = collections.OrderedDict()
        keys = []
        for item in self.dictionary.keys():

            if item == self.currentFile.keys()[0]:
                pass
            else:
                newDict[item] = self.dictionary[item]
                keys.append(self.currentFile)
                
        keys = np.delete(self.currentFiles, np.nonzero(self.currentFiles == self.currentFile.keys()[0]))
        wx.CallAfter(pub.sendMessage, "RemoveFiles", keys)
        wx.CallAfter(pub.sendMessage, "InputFiles", keys)
        if len(keys) > 0:
            wx.CallAfter(pub.sendMessage, "ChangeSelection", keys[0])

        #pub.sendMessage(("InputFiles"), keys)
        self.dictionary = newDict
        wx.CallAfter(pub.sendMessage, "UpdateInput", newDict)
        


    def TransferInput(self):
        wx.CallAfter(pub.sendMessage, "GetInputs", self.dictionary)
    
    def OnRun(self, e):
        """Runs the simulation and opens files if needed"""
        wx.CallAfter(pub.sendMessage, "ClearTabs", "True")
        self.TransferInput()
        logging.debug("Entered path: %s", self.project)
        
        dictionary = ProjectToParams(self.project)

        SimulationThread(self, self.project, self.folderControl, self.sensitivityControl, self.performSensitivityAnalysis)
        

        dlg = RuntimeDialog(self, dictionary, self.performSensitivityAnalysis)
        dlg.ShowModal()
        
        '''
        path = os.path.dirname(os.path.realpath("OPTIONS.csv"))
        path = os.path.join(path, "SimOutputMacro1110.xlsm")        
        
        excel = win32com.client.DispatchEx("Excel.Application")
        workbook = excel.workbooks.open(path)
        excel.run("ConsolidateData")
        excel.Visible = True
        workbook.Close(SaveChanges=1)
        excel.Quit
        '''
        

        
        
    
    def OnAbout(self, e):
        message = "A motorcycle simulation tool used to give users data about motorcycles with user specified parameters."
        message = message + os.linesep + os.linesep + "Created by: Nathan Lord, Sean Harrington, Ishmeet Grewal, Anil Ozyalcin"
        dialogBox = wx.MessageDialog(self, message, "About SIMBA")
        dialogBox.ShowModal() # Show it
        dialogBox.Destroy() #Destroy it when finished
        
    def OnExit(self, e):
        logging.info("ENDING automation.py" + os.linesep + os.linesep)
        logging.shutdown()
        self.Close(True)
    
    def SA_Checkbox_Event(self, e):
        if e.IsChecked():
            self.performSensitivityAnalysis = True
        else:
            self.performSensitivityAnalysis = False

    
    
        
###############################################################################


        
class InputPanel(scrolled.ScrolledPanel):
    """Left panel in WIP GUI window that manages all the import tools"""
    def __init__(self, parent, *args, **kwargs):
        scrolled.ScrolledPanel.__init__(self, parent, *args, **kwargs)
        self.parent = parent


        self.dictionary = dict()
        self.fileToFile = dict()
        self.fileNames = []

        pub.subscribe(self.SetDictionary, ("UpdateInput"))
        pub.subscribe(self.Update, ("InputFiles"))
        pub.subscribe(self.ClearFiles, ("RemoveFiles"))
        pub.subscribe(self.SetComboFile, ("ChangeSelection"))
        
        
        #self.toolbar = wx.ToolBar(self, wx.ID_ANY, size = (2000, 32))
        #self.toolbar.SetToolBitmapSize( ( 21, 21 ) )
        self.dropDownList = wx.ComboBox(self, -1, style = wx.CB_READONLY|wx.TRANSPARENT_WINDOW, size = (275,22))
        self.Bind(wx.EVT_COMBOBOX, self.UpdateFields)
        #self.toolbar.AddControl()
        #self.toolbar.AddControl(self.dropDownList)
        
        self.topHSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.topHSizer.Add(wx.StaticText(self, wx.ID_ANY, "      Parameter File     "))
        self.topHSizer.Add(self.dropDownList)
        
        #self.Bind(wx.EVT_TOOL_ENTER, self.resetStatusBar)
                
        self.values=[]
        self.keys=[]
        
        
        
        #Create Sizers    
        self.vSizer = wx.BoxSizer(wx.VERTICAL)
        self.hSizer= wx.BoxSizer(wx.HORIZONTAL)
        self.vSizer1 = wx.BoxSizer(wx.VERTICAL)
        
        self.vSizer.AddSpacer(10)
        self.vSizer.Add(self.topHSizer)        
        
        self.vSizer1.AddSpacer(2)
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Gearing (ratio)" ,size=(180,25)))        
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Step (seconds)",size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Total Time (seconds)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Top Lean Angle (degrees)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Tyre A" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Tyre B" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Tyre C" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Rolling Resistance" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Rider Mass (kg)" ,size=(180,25)))      
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Bike Mass (kg)",size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Air Resistance",size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Gravity (m/s^2)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Frontal Area (m^2)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Top Motor Current (amps)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Top RPM (RPM)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Max Distance Travel (meters)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Battery Efficiency" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Motor Torque Constant (Nm/amps rms)" ,size=(215,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Motor RPM Constant (RPM/Voltage)" ,size=(215,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Motor Top Power (watts)" ,size=(215,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Motor Thermal Conductivity (W/m*C)" ,size=(215,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Motor Heat Capacity (J/C)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Max Motor Temp (C)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Coolant Temp (C)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Battery Max Current (A)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Max Amphours (Amphours)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Cell Amount in Series" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Distance to Altitude Lookup" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Distance to Speed Lookup" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Motor Efficiency Lookup" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Motor Controller Eff Lookup" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "SOC to Voltage Lookup" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Throttlemap Lookup" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Lean Angle Lookup" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Chain Efficiency Lookup" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Corner Radius Lookup", size=(180,25)))

        self.vSizer1.AddSpacer(3)
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Comments", size=(215,25)))
 
        
        self.vSizer2 = wx.BoxSizer(wx.VERTICAL)
        
        self.p0 = wx.TextCtrl(self, size=(150,25))
        self.p1 = wx.TextCtrl(self, size=(150,25))
        self.p2 = wx.TextCtrl(self, size=(150,25))
        self.p3 = wx.TextCtrl(self, size=(150,25))
        self.p4 = wx.TextCtrl(self, size=(150,25))
        self.p5 = wx.TextCtrl(self, size=(150,25))
        self.p6 = wx.TextCtrl(self, size=(150,25))
        self.p7 = wx.TextCtrl(self, size=(150,25))
        self.p8 = wx.TextCtrl(self, size=(150,25))
        self.p9 = wx.TextCtrl(self, size=(150,25))
        self.p10 = wx.TextCtrl(self, size=(150,25))
        self.p11 = wx.TextCtrl(self, size=(150,25))
        self.p12 = wx.TextCtrl(self, size=(150,25))
        self.p13 = wx.TextCtrl(self, size=(150,25))
        self.p14 = wx.TextCtrl(self, size=(150,25))
        self.p15 = wx.TextCtrl(self, size=(150,25))
        self.p16 = wx.TextCtrl(self, size=(150,25))
        self.p17 = wx.TextCtrl(self, size=(150,25))
        self.p18 = wx.TextCtrl(self, size=(150,25))
        self.p19 = wx.TextCtrl(self, size=(150,25))
        self.p20 = wx.TextCtrl(self, size=(150,25))
        self.p21 = wx.TextCtrl(self, size=(150,25))
        self.p22 = wx.TextCtrl(self, size=(150,25))
        self.p23 = wx.TextCtrl(self, size=(150,25))
        self.p24 = wx.TextCtrl(self, size=(150,25))
        self.p25 = wx.TextCtrl(self, size=(150,25))
        self.p26 = wx.TextCtrl(self, size=(150,25))
        self.p27 = wx.TextCtrl(self, size=(150,25))
        self.p28 = wx.TextCtrl(self, size=(150,25))
        self.p29 = wx.TextCtrl(self, size=(150,25))
        self.p30 = wx.TextCtrl(self, size=(150,25))
        self.p31 = wx.TextCtrl(self, size=(150,25))
        self.p32 = wx.TextCtrl(self, size=(150,25))
        self.p33 = wx.TextCtrl(self, size=(150,25))
        self.p34 = wx.TextCtrl(self, size=(150,25))
        self.p35 = wx.TextCtrl(self, size=(150,25))
        self.comments = wx.TextCtrl(self, size = (390,160), style = wx.TE_MULTILINE)
        
        self.textCtrlList = (self.p0, self.p1, self.p2, self.p3, self.p4, self.p5,
                        self.p6, self.p7, self.p8, self.p9, self.p10, self.p11,
                        self.p12, self.p13, self.p14, self.p15,
                        self.p16, self.p17, self.p18, self.p19,
                        self.p20, self.p21, self.p22, self.p23, self.p24,
                        self.p25, self.p26, self.p27, self.p28, self.p29, self.p30,
                        self.p31, self.p32, self.p33, self.p34, self.p35,
                        self.comments)
        
        for i in xrange(len(self.textCtrlList) - 1):
            self.textCtrlList[i+1].MoveAfterInTabOrder(self.textCtrlList[i])

        self.p0.Bind(wx.EVT_TEXT, self.UpdateP0)
        self.p1.Bind(wx.EVT_TEXT, self.UpdateP1)
        self.p2.Bind(wx.EVT_TEXT, self.UpdateP2)
        self.p3.Bind(wx.EVT_TEXT, self.UpdateP3)
        self.p4.Bind(wx.EVT_TEXT, self.UpdateP4)
        self.p5.Bind(wx.EVT_TEXT, self.UpdateP5)
        self.p6.Bind(wx.EVT_TEXT, self.UpdateP6)
        self.p7.Bind(wx.EVT_TEXT, self.UpdateP7)
        self.p8.Bind(wx.EVT_TEXT, self.UpdateP8)
        self.p9.Bind(wx.EVT_TEXT, self.UpdateP9)
        self.p10.Bind(wx.EVT_TEXT, self.UpdateP10)
        self.p11.Bind(wx.EVT_TEXT, self.UpdateP11)
        self.p12.Bind(wx.EVT_TEXT, self.UpdateP12)
        self.p13.Bind(wx.EVT_TEXT, self.UpdateP13)
        self.p14.Bind(wx.EVT_TEXT, self.UpdateP14)
        self.p15.Bind(wx.EVT_TEXT, self.UpdateP15)
        self.p16.Bind(wx.EVT_TEXT, self.UpdateP16)
        self.p17.Bind(wx.EVT_TEXT, self.UpdateP17)
        self.p18.Bind(wx.EVT_TEXT, self.UpdateP18)
        self.p19.Bind(wx.EVT_TEXT, self.UpdateP19)
        self.p20.Bind(wx.EVT_TEXT, self.UpdateP20)
        self.p21.Bind(wx.EVT_TEXT, self.UpdateP21)
        self.p22.Bind(wx.EVT_TEXT, self.UpdateP22)
        self.p23.Bind(wx.EVT_TEXT, self.UpdateP23)
        self.p24.Bind(wx.EVT_TEXT, self.UpdateP24)
        self.p25.Bind(wx.EVT_TEXT, self.UpdateP25)
        self.p26.Bind(wx.EVT_TEXT, self.UpdateP26)
        self.p27.Bind(wx.EVT_TEXT, self.UpdateP27)
        self.p28.Bind(wx.EVT_TEXT, self.UpdateP28)
        self.p29.Bind(wx.EVT_TEXT, self.UpdateP29)
        self.p30.Bind(wx.EVT_TEXT, self.UpdateP30)
        self.p31.Bind(wx.EVT_TEXT, self.UpdateP31)
        self.p32.Bind(wx.EVT_TEXT, self.UpdateP32)
        self.p33.Bind(wx.EVT_TEXT, self.UpdateP33)
        self.p34.Bind(wx.EVT_TEXT, self.UpdateP34)
        self.p35.Bind(wx.EVT_TEXT, self.UpdateP35)
        self.comments.Bind(wx.EVT_TEXT, self.UpdateComments)
        

        
        
            
        for i in xrange(len(self.textCtrlList)-1):
            self.vSizer2.Add(self.textCtrlList[i])
            
        self.hSizerTopRow = wx.BoxSizer(wx.HORIZONTAL)
        self.commentsSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.commentsSizer.AddSpacer(15)
        self.commentsSizer.Add(self.comments)

        #Add Both columns to Horizontal Sizer
        self.hSizer.AddSpacer((20,-1))        
        self.hSizer.Add(self.vSizer1)
        self.hSizer.AddSpacer((20,-1))
        self.hSizer.Add(self.vSizer2)
        
        #Add Horizontal Sizers to Vertical Sizer
        #self.vSizer.Add(self.toolbar)
        self.vSizer.AddSpacer((-1,10))        
        
        #self.vSizer.Add(self.buttonRun)

        self.vSizer.Add(self.hSizer)
        self.vSizer.Add(self.commentsSizer)
        
        self.SetSizer(self.vSizer)
        
        #self.toolbar.Realize()
        self.SetAutoLayout(1)
        self.vSizer.Fit(self)
        self.Layout()
        self.SetAutoLayout(1)
        self.SetupScrolling(scroll_x = False, scroll_y = True, rate_x=20, rate_y=20, scrollToTop=True)
    
    
    def resetStatusBar(self, e):
        self.dropDownList.Show()
    
    def Update(self, msg): 
        

        self.fileNames = msg.data
        for file in self.fileNames:
            if file not in self.dropDownList.GetItems():
                self.dropDownList.Append(file)
                self.dropDownList.SetSelection(0)
            
     
    def ClearFiles(self, msg):
        
        msg = msg.data
        self.dropDownList.Clear()    

            
        
    def SetDictionary(self, msg):
        self.dictionary = msg.data
        index = 0
        for file in self.dictionary:   
            self.fileToFile[self.fileNames[index]] = file 
            index = index + 1
          
        self.fileToFile
        if len(self.dictionary) > 0:
            
            self.UpdateFields(wx.EVT_COMBOBOX)
            wx.CallAfter(pub.sendMessage, "DisableDelete", False)
            #pub.sendMessage(("DictFromInput"), self.dictionary)

        else:
            for i in xrange(len(self.textCtrlList)):
                self.textCtrlList[i].SetValue("")            
            
            self.dropDownList.Clear()
            wx.CallAfter(pub.sendMessage, "DisableDelete", True)
            


        
    def SetComboFile(self, msg):
        msg = msg.data
        #if self.dropDownList.GetCount() < 2:
        try:
            self.dropDownList.SetSelection(self.dropDownList.GetItems().index(msg))
        except:
            self.dropDownList.SetSelection(self.dropDownList.GetItems().index(msg.keys()[0]))
            
        
    """Button Run Function"""
    def UpdateFields(self,event):
        
        self.values = []
        wx.CallAfter(pub.sendMessage, "InputFile", self.fileToFile) 
        currentFile = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]
        fileDict = dict()
        fileDict[self.fileToFile[self.dropDownList.GetValue()]] = currentFile
        wx.CallAfter(pub.sendMessage, "CurrentFile", fileDict)
        
        
        for k,v in currentFile.iteritems():
            try:
                self.values.append(v[0])
            except:
                self.values.append("")
        
        try:
            self.p0.ChangeValue(str(currentFile["gearing"][0]))  
        except:
            self.p0.ChangeValue('')
        try:
            self.p1.ChangeValue(str(currentFile["step"][0]))
        except:
            self.p1.ChangeValue('')
        try:
            self.p2.ChangeValue(str(currentFile["total_time"][0]))   
        except:
            self.p2.ChangeValue('')
        try:
            self.p3.ChangeValue(str(currentFile["top_lean_angle"][0]))
        except:
            self.p3.ChangeValue('')
        try:
            self.p4.ChangeValue(str(currentFile["tyreA"][0]))   
        except:
            self.p4.ChangeValue('')
        try:
            self.p5.ChangeValue(str(currentFile["tyreB"][0]))
        except:
            self.p5.ChangeValue('')
        try:
            self.p6.ChangeValue(str(currentFile["tyreC"][0]))      
        except:
            self.p6.ChangeValue('')
        try:
            self.p7.ChangeValue(str(currentFile["rolling_resistance"][0]))
        except:
            self.p7.ChangeValue('')
        try:
            self.p8.ChangeValue(str(currentFile["rider_mass"][0]))  
        except:
            self.p8.ChangeValue('')
        try:
            self.p9.ChangeValue(str(currentFile["bike_mass"][0]))
        except:
            self.p9.ChangeValue('')
        try:
            self.p10.ChangeValue(str(currentFile["air_resistance"][0]))  
        except:
            self.p10.ChangeValue('')
        try:
            self.p11.ChangeValue(str(currentFile["gravity"][0])) 
        except:
            self.p11.ChangeValue('')
        try:
            self.p12.ChangeValue(str(currentFile["frontal_area"][0]))
        except:
            self.p12.ChangeValue('')
        try:
            self.p13.ChangeValue(str(currentFile["top_motor_current"][0]))  
        except:
            self.p13.ChangeValue('')
        try:
            self.p14.ChangeValue(str(currentFile["top_rpm"][0]))
        except:
            self.p14.ChangeValue('')
        try:
            self.p15.ChangeValue(str(currentFile["max_distance_travel"][0]))
        except:
            self.p15.ChangeValue('')
        try:
            self.p16.ChangeValue(str(currentFile["battery_efficiency"][0]))
        except:
            self.p16.ChangeValue('')
        try:
            self.p17.ChangeValue(str(currentFile["motor_torque_constant"][0]))    
        except:
            self.p17.ChangeValue('')
        try:
            self.p18.ChangeValue(str(currentFile["motor_rpm_constant"][0]))
        except:
            self.p18.ChangeValue('')
        try:
            self.p19.ChangeValue(str(currentFile["motor_top_power"][0]))
        except:
            self.p19.ChangeValue('')
        try:
            self.p20.ChangeValue(str(currentFile["motor_thermal_conductivity"][0]))
        except:
            self.p20.ChangeValue('')
        try:
            self.p21.ChangeValue(str(currentFile["motor_heat_capacity"][0]))
        except:
            self.p21.ChangeValue('')
        try:
            self.p22.ChangeValue(str(currentFile["max_motor_temp"][0]))
        except:
            self.p22.ChangeValue('')
        try:
            self.p23.ChangeValue(str(currentFile["coolant_temp"][0]))
        except:
            self.p23.ChangeValue('')
        try:
            self.p24.ChangeValue(str(currentFile["batt_max_current"][0]))
        except:
            self.p24.ChangeValue('')
        try:
            self.p25.ChangeValue(str(currentFile["max_amphour"][0]))
        except:
            self.p25.ChangeValue('')
        try:
            self.p26.ChangeValue(str(currentFile["series_cells"][0]))
        except:
            self.p26.ChangeValue('')
        try:
            self.p27.ChangeValue(str(currentFile["dist_to_alt_lookup"][0]))
        except:
            self.p27.ChangeValue('')
        try:
            self.p28.ChangeValue(str(currentFile["dist_to_speed_lookup"][0]))
        except:
            self.p28.ChangeValue('')
        try:
            self.p29.ChangeValue(str(currentFile["motor_eff_lookup"][0]))
        except:
            self.p29.ChangeValue('')
        try:
            self.p30.ChangeValue(str(currentFile["motor_controller_eff_lookup"][0]))
        except:
            self.p30.ChangeValue('')
        try:
            self.p31.ChangeValue(str(currentFile["soc_to_voltage_lookup"][0]))
        except:
            self.p31.ChangeValue('')
        try:
            self.p32.ChangeValue(str(currentFile["throttlemap_lookup"][0]))
        except:
            self.p32.ChangeValue('')
        try:
            self.p33.ChangeValue(str(currentFile["lean_angle_lookup"][0]))
        except:
            self.p33.ChangeValue('')
        try:
            self.p34.ChangeValue(str(currentFile["chain_efficiency_lookup"][0])) 
        except:
            self.p34.ChangeValue('')
        try:
            self.p35.ChangeValue(str(currentFile["corner_radius_lookup"][0])) 
        except:
            self.p35.ChangeValue('')
        try:
            self.comments.ChangeValue(str(currentFile["comments"][0]))
        except:
            self.comments.ChangeValue('')

    
    def UpdateP0 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['gearing'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['gearing'] = [self.p0.GetValue()]
            wx.CallAfter(pub.sendMessage, "DictFromInput", self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Gearing changed from " + str(previousValue) + " to " + self.p0.GetValue()
            wx.CallAfter(pub.sendMessage, "AddStatus", msg)  
        except:
            pass
        
    def UpdateP1 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['step'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['step'] = [self.p1.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Step changed from " + str(previousValue) + " to " + self.p1.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP2 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['total_time'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['total_time'] = [self.p2.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Total Time changed from " + str(previousValue) + " to " + self.p2.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP3 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['top_lean_angle'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['top_lean_angle'] = [self.p3.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Top Lean Angle changed from " + str(previousValue) + " to " + self.p3.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP4 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['tyreA'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['tyreA'] = [self.p4.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Tyre A changed from " + str(previousValue) + " to " + str(self.p4.GetValue())
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP5 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['tyreB'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['tyreB'] = [self.p5.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Tyre B changed from " + str(previousValue) + " to " + str(self.p5.GetValue())
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP6 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['tyreC'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['tyreC'] = [self.p6.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Tyre C changed from " + str(previousValue) + " to " + str(self.p6.GetValue())
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP7 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['rolling_resistance'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['rolling_resistance'] = [self.p7.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Rolling Resistance changed from " + str(previousValue) + " to " + self.p7.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP8 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['rider_mass'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['rider_mass'] = [self.p8.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Rider Mass changed from " + str(previousValue) + " to " + self.p8.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP9 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['bike_mass'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['bike_mass'] = [self.p9.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Bike Mass changed from " + str(previousValue) + " to " + self.p9.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP10 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['air_resistance'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['air_resistance'] = [self.p10.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Air Resistance changed from " + str(previousValue) + " to " + self.p10.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
               
    def UpdateP11 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['gravity'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['gravity'] = [self.p11.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Gravity changed from " + str(previousValue) + " to " + self.p11.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP12 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['frontal_area'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['frontal_area'] = [self.p12.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Frontal Area changed from " + str(previousValue) + " to " + self.p12.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP13 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['top_motor_current'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['top_motor_current'] = [self.p13.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Top Motor Current changed from " + str(previousValue) + " to " + self.p13.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
        
    def UpdateP14 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['top_rpm'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['top_rpm'] = [self.p14.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Top RPM changed from " + str(previousValue) + " to " + self.p14.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP15 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['max_distance_travel'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['max_distance_travel'] = [self.p15.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Max Distance Travel changed from " + str(previousValue) + " to " + self.p15.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP16 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['battery_efficiency'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['battery_efficiency'] = [self.p16.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Battery Efficiency changed from " + str(previousValue) + " to " + self.p16.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP17 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_torque_constant'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_torque_constant'] = [self.p17.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Motor Torque Constant changed from " + str(previousValue) + " to " + self.p17.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP18 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_rpm_constant'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_rpm_constant'] = [self.p18.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Motor RPM Constant changed from " + str(previousValue) + " to " + self.p18.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP19 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_top_power'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_top_power'] = [self.p19.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Motor Top Power changed from " + str(previousValue) + " to " + self.p19.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
        
    def UpdateP20 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_thermal_conductivity'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_thermal_conductivity'] = [self.p20.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Motor Thermal Conductivity changed from " + str(previousValue) + " to " + self.p20.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP21 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_heat_capacity'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_heat_capacity'] = [self.p21GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Motor Heat Capacity changed from " + str(previousValue) + " to " + self.p21.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
    
    def UpdateP22 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['max_motor_temp'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['max_motor_temp'] = [self.p22.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Max Motor Temp changed from " + str(previousValue) + " to " + self.p22.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass

    def UpdateP23 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['coolant_temp'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['coolant_temp'] = [self.p23.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Coolant Temp changed from " + str(previousValue) + " to " + self.p23.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass    

    def UpdateP24 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['batt_max_current'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['batt_max_current'] = [self.p24.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Battery Max Current changed from " + str(previousValue) + " to " + self.p24.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass    
        
    def UpdateP25 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['max_amphour'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['max_amphour'] = [self.p25.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Max Amphour changed from " + str(previousValue) + " to " + self.p25.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP26 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['series_cells'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['series_cells'] = [self.p26.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Cell Amount in Series changed from " + str(previousValue) + " to " + self.p26.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass  
        
    def UpdateP27 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['dist_to_alt_lookup'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['dist_to_alt_lookup'] = [self.p27.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Distance to Altitude Lookup changed from " + str(previousValue) + " to " + self.p27.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass  
        
    def UpdateP28 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['dist_to_speed_lookup'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['dist_to_speed_lookup'] = [self.p28.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Distance to Speed Lookup changed from " + str(previousValue) + " to " + self.p28.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
    
    def UpdateP29 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_eff_lookup'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_eff_lookup'] = [self.p29.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Motor Efficiency Lookup changed from " + str(previousValue) + " to " + self.p29.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass 
    
    def UpdateP30 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_controller_eff_lookup'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_controller_eff_lookup'] = [self.p30.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Motor Controller Efficiency Lookup changed from " + str(previousValue) + " to " + self.p30.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass 
    
    def UpdateP31 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['soc_to_voltage_lookup'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['soc_to_voltage_lookup'] = [self.p31.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "SOC to Voltage Lookup changed from " + str(previousValue) + " to " + self.p31.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass 
    
    def UpdateP32 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['throttlemap_lookup'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['throttlemap_lookup'] = [self.p32.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Throttle Map Lookup changed from " + str(previousValue) + " to " + self.p32.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass 
        
    def UpdateP33 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['lean_angle_lookup'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['lean_angle_lookup'] = [self.p33.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Lean Angle Lookup changed from " + str(previousValue) + " to " + self.p33.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass 
        
    def UpdateP34 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['chain_efficiency_lookup'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['chain_efficiency_lookup'] = [self.p34.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Chain Efficiency Lookup changed from " + str(previousValue) + " to " + self.p34.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP35 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['corner_radius_lookup'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['corner_radius_lookup'] = [self.p35.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Corner Radius Lookup changed from " + str(previousValue) + " to " + self.p35.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateComments (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['comments'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['comments'] = [self.comments.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            #msg = datetime.now().strftime('%H:%M:%S') + ": " + "Top Power changed from " + str(previousValue) + " to " + self.p23.GetValue()
            #pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
     
##############################################################################        

class OutputPanel(wx.Panel):
    """Right panel in WIP GUI window that shows all the results after running the simulation"""
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent        
        
        ## Insert components in the panel after here
        pub.subscribe(self.CreateTab, ("fileNames.key"))
        pub.subscribe(self.PlugInData, ("fileName.data"))
        pub.subscribe(self.ClearTabs, ("ClearTabs"))
        
        
        self.notebook = wx.Notebook(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer)
        self.Layout()

        
    
    def CreateTab(self, msg):
        self.page = NewTabPanel(self.notebook)
        self.notebook.AddPage(self.page, msg.data)
        
    def PlugInData(self, msg):
        
        data = msg.data
        #Run through the dictionary passed, individually assign each cell in grid
        column = 0;
        keys = data.keys()

        self.page.myGrid.CreateGrid(len(data[keys[0]]),len(keys))

        for key in data:
            
            self.page.myGrid.SetColLabelValue(column, key)
            row = 0
            
            if not isinstance(data[key], float):
                for value in data[key]:
                    if not type(value) == str:
                        value = repr(round(value, 3))
    
                    self.page.myGrid.SetCellValue(row, column, value)
                    row = row + 1
                column = column + 1
                
            else:
                value = repr(round(data[key], 3))
                self.page.myGrid.SetCellValue(row, column, value)
                column = column + 1
                
                
        
        self.page.myGrid.AutoSizeColumns()

        
    def ClearTabs(self, msg):
        if msg.data == "True":   
            try:
                self.notebook.DeleteAllPages()
                self.page.myGrid.ClearGrid()
            except:
                pass
            
            
###############################################################################            
        
class StatusPanel(wx.Panel):
    """Panel below InputPanel and OutputPanel that shows simulation status messages"""
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        pub.subscribe(self.AddStatus, ("AddStatus"))

        self.panelLabel = wx.StaticText(self, wx.ID_ANY, "Status Messages",size=(-1,-1))
        self.statusTextCtrl = wx.richtext.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER)
        #self.statusTextCtrl = wx.TextCtrl(self, -1,size=(200, 100), style= wx.TE_RICH | wx.TE_MULTILINE ^ wx.TE_READONLY)
        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.panelLabel.SetFont(font)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panelLabel, 0, wx.ALL, 5)
        sizer.Add(self.statusTextCtrl, 1, wx.ALL|wx.EXPAND)
        
        
        self.SetSizer(sizer)
        self.Layout()
      

        
    def AddStatus(self, msg):
        
        if "WARNING" in msg.data:
            # Get the status string not including the time stamp
            if msg.data[10:] not in self.statusTextCtrl.GetValue():
                self.statusTextCtrl.BeginTextColour((255, 0, 0))
                self.statusTextCtrl.WriteText(msg.data)
                self.statusTextCtrl.EndTextColour()
                self.statusTextCtrl.Newline()
        else:
            self.statusTextCtrl.WriteText(msg.data)
            self.statusTextCtrl.Newline()
        
        self.statusTextCtrl.ShowPosition(self.statusTextCtrl.GetLastPosition())
        
##############################################################################        
    
##############################################################################

class NewTabPanel(wx.Panel):
    """Generates panel for each tab"""
    def __init__(self,parent):
        
        wx.Panel.__init__(self, parent= parent, id=wx.ID_ANY)
        
        self.myGrid = gridlib.Grid(self)
        self.myGrid.EnableEditing(False)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.myGrid, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)
        self.Layout()


########################################################################
class SimulationThread(Thread):
    """Test Worker Thread Class."""
 
    #----------------------------------------------------------------------
    def __init__(self, parent, project, folderControl, sensitivityControl, performAnalysis):
        """Init Worker Thread Class."""
        
        pub.subscribe(self.stopThread, "AbortThread")

        self.folderControl = folderControl
        self.sensitivityControl = sensitivityControl
        
        Thread.__init__(self)
        self._parent = parent
        self._want_abort = 0
        global closeWorkerThread
        closeWorkerThread = 0
        self.project = project

        self.performSensitivityAnalysis = performAnalysis
        self.setDaemon(1)
        self.start()    # start the thread


    #----------------------------------------------------------------------
    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread.
        dictionary = ProjectToParams(self.project)
        
        inFiles = np.loadtxt(open(self.project, "rb"), dtype = 'string', delimiter = ',')
        if not os.path.exists(self.folderControl.GetValue()):
            os.makedirs(self.folderControl.GetValue())
        
        inFiles[1,3] = self.folderControl.GetValue()
        # Sensitivity Analysis Function calls
        #percentChange = 15
        if self.performSensitivityAnalysis:
            sensitivityValue = self.sensitivityControl.GetValue()
            wx.CallAfter(pub.sendMessage, "TransferSensitivityValue", sensitivityValue)
            decimalEquiv = self.sensitivityControl.GetValue() / 100.0
            saDict = collections.OrderedDict()            
            saDict = SensitivityAnalysis(deepcopy(dictionary), decimalEquiv)
            if type(saDict) is  None:
                return
            arrays = CreateSortArrays(saDict)
            wx.CallAfter(pub.sendMessage, "TransferSortArrays", arrays)
            #pub.sendMessage(("TransferSortArrays"), arrays)
            wx.CallAfter(pub.sendMessage, "TransferSADictionary", saDict)            
        
        outputDict = sim.Simulation(deepcopy(dictionary))

        folder = self.folderControl.GetValue()
        wx.CallAfter(pub.sendMessage, "TransferOutputDirectory", folder)
        
                
        outputDirectory = self.folderControl.GetValue()
        logging.debug("Entered out path: %s",outputDirectory)
        OutputFile(outputDirectory, outputDict)
        #OutputFile(outputDirectory, senseAnalysisDict)
        WriteFolder(self.project,outputDirectory)
        
        # Gather filenames and value for quick values
        fileNames = np.array(outputDict.keys())
        #fileNames = np.append(outputDict.keys(), senseAnalysisDict.keys())
        #resultsWindow = QuickResultsWindow(None, "Quick Results")
        testWindow.Freeze()
        index = 1
        for key in fileNames:
            inFiles[index, 2] = dictionary[key]["comments"][0]
            msg = key
            wx.CallAfter(pub.sendMessage, "fileNames.key", msg)
            #pub.sendMessage(("fileNames.key"), msg)     
            
            if outputDict.has_key(key):
                currentDict = outputDict[key]
            #else:         # Used to make quick value tabs for senseAnalysis files
            #    currentDict = senseAnalysisDict[key]
            msg = currentDict
            wx.CallAfter(pub.sendMessage, "fileName.data", msg)
            #pub.sendMessage(("fileName.data"), msg)         
            index = index + 1
        
        try:
            np.savetxt(self.project, inFiles, delimiter=",", fmt="%s")
        except:
            logging.critical("Could not save project at the end of the simulation")
            
        #SA_Frame.Show()
        SA_Frame.Raise()
        testWindow.Thaw()
            
        
    def stopThread(self, msg):
        print "Trying to STOP!"
        self.stopped = True
        self._want_abort = 1
        global closeWorkerThread
        closeWorkerThread = 1
            
 
########################################################################

########################################################################
class RuntimeDialog(wx.Dialog):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, parent, project, performAnalysis):
        """Constructor"""
        wx.Dialog.__init__(self, parent, title="Simulation Progress")
        self.count = 0
 
        if performAnalysis is True:
            # Three updates in simulation, x amount of parameters, times 2 for sensitivity report, number of files
            self.amountOfUpdates = (len(project.keys()) * 3 * len(project[project.keys()[0]].keys()) * 2) + (len(project.keys()) * 3)
        else:
            # Three increments in each individual file simulation run
            self.amountOfUpdates = len(project.keys())*3

        self.progress = wx.Gauge(self, range=self.amountOfUpdates, size = (400, 20), pos = self.Center())
        #self.runningSimText = wx.StaticText(self, wx.ID_ANY, "Running Simulation and Sensitivity Analysis")
        #self.runningSimText.SetFont(wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD))
        #self.runningSimText.SetForegroundColour('GREEN')
        self.notificationText = wx.StaticText(self, wx.ID_ANY, "Please wait, this could take a few minutes...")
        self.progressText = wx.StaticText(self, wx.ID_ANY, "Progress: " + str(self.progress.GetValue()/self.amountOfUpdates) + "%")
        sizer = wx.BoxSizer(wx.VERTICAL)
        horizontalSizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontalSizer.AddSpacer(10)
        sizer.AddSpacer(10)
        sizer.Add(self.notificationText)
        sizer.AddSpacer(2)
        sizer.Add(self.progressText)
        sizer.AddSpacer(5)
        sizer.Add(self.progress, 0, wx.EXPAND)
        sizer.AddSpacer(10)
        horizontalSizer.Add(sizer)
        horizontalSizer.AddSpacer(10)
        self.SetSizer(horizontalSizer)
        self.Fit()
        self.RestartDialog()
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        # create a pubsub listener
        pub.subscribe(self.updateProgress, "update")

    #----------------------------------------------------------------------
    def updateProgress(self, msg):
        """
        Update the progress bar
        """
        self.count += 1
 
        if self.count >= self.amountOfUpdates:
            self.Hide()
 
        self.progress.SetValue(self.count)
        percentProgress = float(self.count) / float(self.amountOfUpdates) * 100
        self.progressText.SetLabel("Progress: " + repr(int(percentProgress)) + "%")
 
    def RestartDialog(self):
        self.count = 0
        self.progress.SetValue(0)
        self.Show()
    
    def OnExit(self, e):
        wx.CallAfter(pub.sendMessage, "AbortThread", "")
        self.Hide()
        
#############################################################


###############################################################################
# GUI Ends Here
###############################################################################
# Main loop and script starts here
###############################################################################

logging.basicConfig(filename="SIMBA_log.txt",format='%(asctime)s - %(levelname)s - %(message)s',level=logging.DEBUG)
logging.info("STARTING automation.py")


app = wx.App(False)
testWindow = MainFrame(None, "SIMBA")
SA_Frame = SensitivityAnalysisFrame(testWindow, "Sensitivity Analysis Results")
#SA_Frame.Show()
#quickWindow = QuickResultsWindow(None, "Quick Results")

msg = datetime.now().strftime('%H:%M:%S') + ": " + "Welcome to SIMBA! Start by creating a new project or opening one that has already been generated"
wx.CallAfter(pub.sendMessage, "AddStatus", msg)  

app.MainLoop()

