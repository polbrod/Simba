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
import collections

from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub
from copy import deepcopy
from datetime import datetime

import sys, subprocess

def dependencies_for_automation():  #Missing imports needed to convert to .exe
    from scipy.sparse.csgraph import _validation


def AdjustParams(dictionary, percentChange):  
    
    resultDict = dict()
    dictionary = deepcopy(dictionary)
    percentChange = float(percentChange) / 100
    
    for file in dictionary:
        
        currentData = deepcopy(dictionary[file])
        percentDown = deepcopy(dictionary[file])
        percentUp = deepcopy(dictionary[file])
        file = file[:-4]
        
        for key in currentData:
            if not isinstance(currentData[key][0], str):
                
                originalValue = currentData[key][0]
                percentDown[key] = originalValue - (originalValue * percentChange)
                resultDict[file + "." + key + ".down.csv"] = percentDown.copy()
                percentUp[key] = originalValue + (originalValue * percentChange)
                resultDict[file + "." + key + ".up.csv"] = percentUp.copy()
                percentDown[key] = originalValue
                percentUp[key] = originalValue
            
    return resultDict
    
def FileToParams(inFiles):
    
    optionsFile = inFiles
    logging.info("STARTING FUNCTIONS FileToParams")
    os.chdir(os.path.dirname(os.path.realpath(inFiles)))    
    logging.debug("Options file location passed: %s", inFiles)
    inFiles = np.loadtxt(open(inFiles, "rb"), dtype = 'string', delimiter = ',')
    files = inFiles[1:,0]
    pub.sendMessage(("InputFiles"), files)
    inputDict = collections.OrderedDict()
    
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
            GUIdialog = wx.MessageDialog(None, "Unable to load file in " + optionsFile +". Make sure "+ optionsFile + " is correct or specify a new options file", "Error", wx.OK)
            GUIdialog.ShowModal()
            GUIdialog.Destroy()
            raise Exception("File " + fileName + " not found.  Please remove entry or place file in same folder")
            
        fileName = inFiles[completedTransfers,1]      
        params = data[0]    #Creates array of params and inputs
        data = data[1:]     #Creates array of data without headers        
        fileDict = collections.OrderedDict()
    
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
    
    logging.info("STARTING FUNCTION OutputFile")        
    fileNames = np.array(outputDict.keys())
    
    for key in fileNames:
        
        logging.info("Converting dictionary %s to file",key)
        fileName = folderName + "\\" + key
        logging.debug("File will be saved at %s", fileName)
        currentDict = outputDict[key]
        
        print currentDict.keys()
        paramHeaders = np.array(currentDict.keys())  #Turns headers into numpy array

        maxColumnLength = 0 #Find maximum number of rows
        for x in paramHeaders:
            if maxColumnLength < np.size(currentDict[x]):
                maxColumnLength = np.size(currentDict[x])

        values = np.zeros((maxColumnLength,len(paramHeaders)), dtype = '|S50')
                #Creates an "empty" array with the total number of data points

        
        for x in range(len(paramHeaders)):
            currentValues = str(currentDict[paramHeaders[x]][0]) #Gets list of header values
               #Turns list into numpy array
            

            values[0,x] = currentValues       
        
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
        
    np.savetxt(optionsFile, data, delimiter=",", fmt="%s")
    logging.info("%s successfully edited", optionsFile)
##############################################################################
# GUI Starts Here
##############################################################################
class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800,800), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        
        # Load icon
        if hasattr(sys, 'frozen'):
            iconLoc = os.path.join(os.path.dirname(sys.executable),"SIMBA.exe")
            iconLoc = wx.IconLocation(iconLoc,0)
            self.SetIcon(wx.IconFromLocation(iconLoc))
        #else:
         #   iconLoc = os.path.join(os.path.dirname(__file__),__file__)

        # Setting up menu
        filemenu = wx.Menu()
        self.menuAbout = filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        self.menuExit = filemenu.Append(wx.ID_EXIT, "&Exit"," Terminate the program")
        
        toolsmenu = wx.Menu()
        self.menuNewProject = toolsmenu.Append(wx.ID_ANY, "Create New Project", " Create new project including parameter files and necessary components")
        self.menuNewParamFile = toolsmenu.Append(wx.ID_ANY, "New &Parameters File"," Create new parameter file to add to current options file")
        
        
        # Creating menubar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File") #Adds "filemenu" to the MenuBar
        menuBar.Append(toolsmenu, "&Tools")
        
        self.SetMenuBar(menuBar)

        # Set Events
        self.Bind(wx.EVT_MENU, self.OnAbout, self.menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, self.menuExit)
        self.Bind(wx.EVT_MENU, self.CreateNewProject, self.menuNewProject)
        self.Bind(wx.EVT_MENU, self.NewParamsFile, self.menuNewParamFile)


        self.MainPanel = wx.Panel(self,-1)
        self.Panel = Panel1(self)
        
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.Panel)
        
        self.MainPanel.SetSizer(self.mainSizer)
        #self.MainPanel.Fit()
        self.Fit()

        self.Show(True)

    def OnAbout(self,e) :
        pass
        
    def OnExit(self,e):
        logging.info("ENDING automation.py" + os.linesep + os.linesep)
        logging.shutdown()
        self.Close(True)
    
    def ShowNewParams(self, msg):
        
        if msg.data == True:
            self.menuNewParamFile.Enable(True)
        else:
            self.menuNewParamFile.Enable(False)   
        
    def NewParamsFile(self,e):
        newParamsWindow = NewParamsWindow(None, "Create new parameters file")
        newParamsWindow.Show()
        
    def CreateNewProject(self,e):
        newProjectWindow = NewProjectWindow(None, "Create new project")
        newProjectWindow.Show()
        
###############################################################################
        
class IOSplitterPanel(wx.Panel):
    """ Constructs a Vertical splitter window with left and right panels"""
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        splitter = wx.SplitterWindow(self, style = wx.SP_3D| wx.SP_LIVE_UPDATE)
        splitter.SetSashGravity(0.2)
        splitter.SetMinimumPaneSize(20)        
        leftPanel = InputPanel(splitter, style = wx.BORDER_SIMPLE)
        rightPanel = OutputPanel(splitter, style = wx.BORDER_SIMPLE)        

        splitter.SplitVertically(leftPanel, rightPanel) 
        PanelSizer=wx.BoxSizer(wx.VERTICAL)
        PanelSizer.Add(splitter, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(PanelSizer)

########################################################################

class MainFrame(wx.Frame):
    """Constructor"""
    #----------------------------------------------------------------------
    def __init__(self, parent, id):
        wx.Frame.__init__(self, None, title="SIMBA",size=(1000,1000))
        
        pub.subscribe(self.FindCurrentParamFile, ("CurrentFile")) 
        pub.subscribe(self.SetDictionary, ("DictFromInput"))
        self.currentFile = dict()        
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
        newProjectTool = self.toolbar.AddSimpleTool(wx.ID_ANY, newProject_ico, "New Project", "Create a new project")
        self.Bind(wx.EVT_MENU, self.OnNewProject, newProjectTool)              
        
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
        
        addParamFile_ico = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, (20,20))
        addNewParamTool = self.toolbar.AddSimpleTool(wx.ID_ANY, addParamFile_ico, "New Parameter File", "Add new paramter file to project")
        self.Bind(wx.EVT_MENU, self.OnNewParamFile, addNewParamTool)
        
        removeParamFile_ico = wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR, (20,20))
        removeNewParamTool = self.toolbar.AddSimpleTool(wx.ID_ANY, removeParamFile_ico, "Remove Parameter File", "Remove parameter file from project")
        self.Bind(wx.EVT_MENU, self.OnRemoveParamFile, removeNewParamTool)
        
        run_ico = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR, (20,20))
        runTool = self.toolbar.AddSimpleTool(wx.ID_ANY, run_ico, "Run Simulation", "Runs the simulation with the opened project")
        self.Bind(wx.EVT_MENU, self.OnRun, runTool)
        
        self.folderControl = wx.TextCtrl(self.toolbar, size = (300,-1))
        self.toolbar.AddControl(self.folderControl) 
        
        
        # Setting up menu
        filemenu = wx.Menu()
        self.menuNewFile = filemenu.Append(wx.ID_NEW, "New Parameter File", "Create a new parameter file for the current project")
        self.menuNewProject = filemenu.Append(wx.ID_ANY, "New Project", "Create a new project")
        self.menuOpenProject = filemenu.Append(wx.ID_OPEN, "Open Project", "Open a project")
        self.menuSave = filemenu.Append(wx.ID_SAVE, "Save file", "Save a parameter file")
        self.menuSaveAll = filemenu.Append(wx.ID_ANY, "Save all", "Save all parameter files")
        self.menuSaveProject = filemenu.Append(wx.ID_ANY, "Save Project", "Save project with all parameter files")
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
        
        ################################################################
        # Define mainsplitter as child of Frame and add IOSplitterPanel and StatusPanel as children
        mainsplitter = wx.SplitterWindow(self, style = wx.SP_3D| wx.SP_LIVE_UPDATE)
        mainsplitter.SetSashGravity(0.5)
        mainsplitter.SetMinimumPaneSize(20)

        splitterpanel = IOSplitterPanel(mainsplitter)
        statusPanel = StatusPanel(mainsplitter, style = wx.BORDER_SIMPLE)

        mainsplitter.SplitHorizontally(splitterpanel, statusPanel)
        windowW, windowH = wx.DisplaySize()
        newH = windowH/3.5
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
    
    def FindCurrentParamFile(self, msg):
        self.currentFile = msg.data
        
    def SetDictionary(self, msg):
        self.dictionary = msg.data
        pub.sendMessage(("UpdateInput"), self.dictionary)
    
    def OnNewProject(self,e):
        #Ask user if they want to save current project
        dlg = wx.MessageDialog(self, "Do you want to save the current project before creating a new one?", style = wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            savedlg = wx.FileDialog(self, "Save project", "", "", ".csv|*.csv", style = wx.FD_SAVE)
            if savedlg.ShowModal() == wx.ID_OK:
                self.filename = savedlg.GetFilename()
                self.dirname = savedlg.GetDirectory()
            #OutputFile(self.optionsControl.GetValue(), self.dictionary)
            
            
        self.dictionary = dict()
        pub.sendMessage(("UpdateInput"), self.dictionary)
    
    def OnOpen(self,e):
        
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "Comma Seperated Value (.csv)|*.csv|Text file (.txt)|*.txt")
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.project = (os.path.join(self.dirname, self.filename))
            
            if os.path.exists(self.project) and self.folderControl.IsEmpty():
                try:
                    data = np.loadtxt(open(self.project, "rb"), dtype = 'string', delimiter=',')
                    self.folderControl.SetValue(data[1,3])
                    
                #Extracts all data from file into variable data
                except:
                    pass
                
        dlg.Destroy()
        self.dictionary = FileToParams(self.project)
        pub.sendMessage(("UpdateInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Opened project " + self.project
        pub.sendMessage(("AddStatus"), msg)  
        
    
    def OnSave(self, e):
        """Saves the current parameter file open in input panel"""
        SaveInput(os.path.dirname(os.path.realpath(self.project)), self.currentFile)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Successfully saved " + self.currentFile
        pub.sendMessage(("AddStatus"), msg)  
    
    def OnSaveAll(self,e):
        """Saves all parameters file in the current project"""
        SaveInput(os.path.dirname(os.path.realpath(self.project)), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Successfully saved all parameter files"
        pub.sendMessage(("AddStatus"), msg)  
    
    def OnNewParamFile(self, e):
        #Get file name from input field
        #create new entry in dictionary with that name
        pass
    
    def OnRemoveParamFile(self, e):
        #If project has a parameter file remove the opened param file in the input panel from the dict
        pass
    
    def OnRun(self, e):
        """Runs the simulation and opens files if needed"""
        pub.sendMessage(("ClearTabs"), "True")
        options = self.project
        logging.debug("Entered path: %s", options)
        
        dictionary = FileToParams(options)
        
        # Sensitivity Analysis Function calls
        #percentChange = 15
        #senseAnalysis = AdjustParams(dictionary, percentChange)
        #senseAnalysisDict = sim.Simulation(senseAnalysis)
        outputDict = sim.Simulation(dictionary)
        
        outputDirectory = self.folderControl.GetValue()
        logging.debug("Entered out path: %s",outputDirectory)
        OutputFile(outputDirectory, outputDict)
        #OutputFile(outputDirectory, senseAnalysisDict)
        WriteFolder(options,outputDirectory)
        
        # Gather filenames and value for quick values
        fileNames = np.array(outputDict.keys())
        #fileNames = np.append(outputDict.keys(), senseAnalysisDict.keys())
        #resultsWindow = QuickResultsWindow(None, "Quick Results")
        
        for key in fileNames:
            msg = key
            pub.sendMessage(("fileNames.key"), msg)      
            
            if outputDict.has_key(key):
                currentDict = outputDict[key]
            #else:         # Used to make quick value tabs for senseAnalysis files
            #    currentDict = senseAnalysisDict[key]
            msg = currentDict
            pub.sendMessage(("fileName.data"), msg)            
            
        
        path = os.path.dirname(os.path.realpath("OPTIONS.csv"))
        path = os.path.join(path, "SimOutputMacro0904.xlsm")        
        
        excel = win32com.client.DispatchEx("Excel.Application")
        workbook = excel.workbooks.open(path)
        excel.run("ConsolidateData")
        excel.Visible = True
        workbook.Close(SaveChanges=1)
        excel.Quit
        
    
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
    

    
    
        



        
class InputPanel(wx.Panel):
    """Left panel in WIP GUI window that manages all the import tools"""
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent


        self.dictionary = dict()
        self.fileToFile = dict()
        self.fileNames = []
        pub.subscribe(self.SetDictionary, ("UpdateInput"))
        pub.subscribe(self.Update, ("InputFiles"))
        
        
        self.toolbar = wx.ToolBar(self, wx.ID_ANY, size = (2000, 32))
        self.toolbar.SetToolBitmapSize( ( 21, 21 ) )
        self.dropDownList = wx.ComboBox(self.toolbar, -1, style = wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.UpdateFields)
        self.toolbar.AddControl(wx.StaticText(self.toolbar, wx.ID_ANY, "      Parameter File     "))
        self.toolbar.AddControl(self.dropDownList)

                
        self.values=[]
        self.keys=[]
        
        
        #Create Sizers    
        self.vSizer = wx.BoxSizer(wx.VERTICAL)
        self.hSizer= wx.BoxSizer(wx.HORIZONTAL)
        self.vSizer1 = wx.BoxSizer(wx.VERTICAL)
        
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Gearing" ,size=(180,25)))        
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Distance to Altitude Lookup",size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Step" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Total Time" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Wheel Radius" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Rolling Resistance" ,size=(180,25)))      
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Rider Mass",size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Bike Mass",size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Distance to Speed Lookup",size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Air Resistance" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Air Density" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Gravity" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Frontal Area" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Top Torque" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Top RPM" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Efficiency" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Max Distance Travel" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Chain Efficiency" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Battery Efficiency" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Motor Torque Constant" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Motor RPM Constant" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Motor Controller Efficiency Lookup" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Motor Efficiency Lookup" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Top Power" ,size=(180,25)))
 
        
        self.vSizer2 = wx.BoxSizer(wx.VERTICAL)
        
        self.p0 = wx.TextCtrl(self, size=(150,25), style = wx.TE_PROCESS_ENTER)
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
        
        self.vSizer2.Add(self.p0)
        self.vSizer2.Add(self.p1)
        self.vSizer2.Add(self.p2)
        self.vSizer2.Add(self.p3)
        self.vSizer2.Add(self.p4)
        self.vSizer2.Add(self.p5)
        self.vSizer2.Add(self.p6)
        self.vSizer2.Add(self.p7)
        self.vSizer2.Add(self.p8)
        self.vSizer2.Add(self.p9)
        self.vSizer2.Add(self.p10)
        self.vSizer2.Add(self.p11)
        self.vSizer2.Add(self.p12)
        self.vSizer2.Add(self.p13)
        self.vSizer2.Add(self.p14)
        self.vSizer2.Add(self.p15)
        self.vSizer2.Add(self.p16)
        self.vSizer2.Add(self.p17)
        self.vSizer2.Add(self.p18)
        self.vSizer2.Add(self.p19)
        self.vSizer2.Add(self.p20)
        self.vSizer2.Add(self.p21)
        self.vSizer2.Add(self.p22)
        self.vSizer2.Add(self.p23)
        
        
        
        
        self.hSizerTopRow = wx.BoxSizer(wx.HORIZONTAL)

        
        #Add Both columns to Horizontal Sizer
        self.hSizer.AddSpacer((20,-1))        
        self.hSizer.Add(self.vSizer1)
        self.hSizer.AddSpacer((20,-1))
        self.hSizer.Add(self.vSizer2)
        
        #Add Horizontal Sizers to Vertical Sizer
        self.vSizer.Add(self.toolbar)
        self.vSizer.AddSpacer((-1,10))        
        
        #self.vSizer.Add(self.buttonRun)

        self.vSizer.Add(self.hSizer)
        
        self.SetSizer(self.vSizer)
        
        self.toolbar.Realize()
        self.SetAutoLayout(1)
        self.vSizer.Fit(self)
        self.Layout()
    
        
        
        
    #################################################################
    def Update(self, msg): 
        
        
        self.fileNames = msg.data
        for file in self.fileNames:
            self.dropDownList.Append(file)
            self.dropDownList.SetSelection(0)
            
        
            
        
    def SetDictionary(self, msg):
        self.dictionary = msg.data
        index = 0
        for file in self.dictionary:         
            self.fileToFile[self.fileNames[index]] = file 
            index = index + 1
            
        if len(self.dictionary) > 0:
            self.UpdateFields(wx.EVT_COMBOBOX)
        else:
            self.p0.SetValue("")        
            self.p1.SetValue("")
            self.p2.SetValue("")        
            self.p3.SetValue("")
            self.p4.SetValue("")        
            self.p5.SetValue("")
            self.p6.SetValue("")        
            self.p7.SetValue("")
            self.p8.SetValue("")        
            self.p9.SetValue("")
            self.p10.SetValue("")        
            self.p11.SetValue("")
            self.p12.SetValue("")        
            self.p13.SetValue("")
            self.p14.SetValue("")        
            self.p15.SetValue("")
            self.p16.SetValue("")
            self.p17.SetValue("")        
            self.p18.SetValue("")
            self.p19.SetValue("")
            self.p20.SetValue("")        
            self.p21.SetValue("")
            self.p22.SetValue("")
            self.p23.SetValue("")
            self.dropDownList.Clear()

        
    
    """Button Run Function"""
    def UpdateFields(self,event):
        
        self.values = []

        currentFile = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]
        fileDict = dict()
        fileDict[self.dropDownList.GetValue()] = currentFile
        pub.sendMessage(("CurrentFile"), fileDict)

        for k,v in currentFile.iteritems():
            self.values.append(v[0])
        

        self.p0.ChangeValue(str(self.values[0]))        
        self.p1.ChangeValue(str(self.values[1]))
        self.p2.ChangeValue(str(self.values[2]))        
        self.p3.ChangeValue(str(self.values[3]))
        self.p4.ChangeValue(str(self.values[4]))        
        self.p5.ChangeValue(str(self.values[5]))
        self.p6.ChangeValue(str(self.values[6]))        
        self.p7.ChangeValue(str(self.values[7]))
        self.p8.ChangeValue(str(self.values[8]))        
        self.p9.ChangeValue(str(self.values[9]))
        self.p10.ChangeValue(str(self.values[10]))        
        self.p11.ChangeValue(str(self.values[11]))
        self.p12.ChangeValue(str(self.values[12]))        
        self.p13.ChangeValue(str(self.values[13]))
        self.p14.ChangeValue(str(self.values[14]))        
        self.p15.ChangeValue(str(self.values[15]))
        self.p16.ChangeValue(str(self.values[16]))
        self.p17.ChangeValue(str(self.values[17]))        
        self.p18.ChangeValue(str(self.values[18]))
        self.p19.ChangeValue(str(self.values[19]))
        self.p20.ChangeValue(str(self.values[20]))        
        self.p21.ChangeValue(str(self.values[21]))
        self.p22.ChangeValue(str(self.values[22]))
        self.p23.ChangeValue(str(self.values[23]))
            
    
    def UpdateP0 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['gearing'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['gearing'] = [self.p0.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Gearing changed from " + str(previousValue) + " to " + self.p0.GetValue()
        pub.sendMessage(("AddStatus"), msg)  
        
    def UpdateP1 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['dist_to_alt_lookup'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['dist_to_alt_lookup'] = [self.p1.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Distance to Altitude Lookup changed from " + str(previousValue) + " to " + self.p1.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP2 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['step'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['step'] = [self.p2.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Step changed from " + str(previousValue) + " to " + self.p2.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP3 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['total_time'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['total_time'] = [self.p3.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Total Time changed from " + str(previousValue) + " to " + self.p3.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP4 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['wheel_radius'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['wheel_radius'] = [self.p4.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Wheel Radius changed from " + str(previousValue) + " to " + str(self.p4.GetValue())
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP5 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['rolling_resistance'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['rolling_resistance'] = [self.p5.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Rolling Resistance changed from " + str(previousValue) + " to " + str(self.p5.GetValue())
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP6 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['rider_mass'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['rider_mass'] = [self.p6.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Rider Mass changed from " + str(previousValue) + " to " + str(self.p6.GetValue())
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP7 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['bike_mass'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['bike_mass'] = [self.p7.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Bike mass changed from " + str(previousValue) + " to " + self.p7.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP8 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['dist_to_speed_lookup'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['dist_to_speed_lookup'] = [self.p8.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Distance to Speed Lookup changed from " + str(previousValue) + " to " + self.p8.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP9 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['air_resistance'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['air_resistance'] = [self.p9.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Air Resistance changed from " + str(previousValue) + " to " + self.p9.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP10 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['air_density'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['air_density'] = [self.p10.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Air Density changed from " + str(previousValue) + " to " + self.p10.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP11 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['gravity'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['gravity'] = [self.p11.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Gravity changed from " + str(previousValue) + " to " + self.p11.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP12 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['frontal_area'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['frontal_area'] = [self.p12.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Frontal Area changed from " + str(previousValue) + " to " + self.p12.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP13 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['top_torque'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['top_torque'] = [self.p13.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Top Torque changed from " + str(previousValue) + " to " + self.p13.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP14 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['top_rpm'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['top_rpm'] = [self.p14.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Top RPM changed from " + str(previousValue) + " to " + self.p14.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP15 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['efficiency'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['efficiency'] = [self.p15.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Efficiency changed from " + str(previousValue) + " to " + self.p15.GetValue()
        pub.sendMessage(("AddStatus"), msg)        
        
    def UpdateP16 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['max_distance_travel'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['max_distance_travel'] = [self.p16.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Max Distance Travel changed from " + str(previousValue) + " to " + self.p16.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP17 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['chain_efficiency'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['chain_efficiency'] = [self.p17.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Chain Efficiency changed from " + str(previousValue) + " to " + self.p17.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP18 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['battery_efficiency'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['battery_efficiency'] = [self.p18.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Battery Efficiency changed from " + str(previousValue) + " to " + self.p18.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP19 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_torque_constant'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_torque_constant'] = [self.p19.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Motor Torque Constant changed from " + str(previousValue) + " to " + self.p19.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP20 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_rpm_constant'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_rpm_constant'] = [self.p20.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Motor RPM Constant changed from " + str(previousValue) + " to " + self.p20.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP21 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_controller_eff_lookup'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_controller_eff_lookup'] = [self.p21.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Motor Controller Efficiency Lookup changed from " + str(previousValue) + " to " + self.p21.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP22 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_eff_lookup'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_eff_lookup'] = [self.p22.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Motor Efficiency Lookup changed from " + str(previousValue) + " to " + self.p22.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
    def UpdateP23 (self, e):
        previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['top_power'][0]
        self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['top_power'] = [self.p23.GetValue()]
        pub.sendMessage(("DictFromInput"), self.dictionary)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Top Power changed from " + str(previousValue) + " to " + self.p23.GetValue()
        pub.sendMessage(("AddStatus"), msg)
        
     
        

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
            
            
          
        
        
        
class StatusPanel(wx.Panel):
    """Panel below InputPanel and OutputPanel that shows simulation status messages"""
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        pub.subscribe(self.AddStatus, ("AddStatus"))

        self.panelLabel = wx.StaticText(self, wx.ID_ANY, "Status Messages",size=(-1,-1))
        self.statusTextCtrl = wx.TextCtrl(self, -1,size=(200, 100), style=wx.TE_MULTILINE ^ wx.TE_READONLY)
        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.panelLabel.SetFont(font)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panelLabel, 0, wx.ALL, 5)
        sizer.Add(self.statusTextCtrl, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer)
        self.Layout()
        
    def AddStatus(self, msg):
        currentTextCtrl = self.statusTextCtrl.GetValue()
        newTextCtrl = currentTextCtrl + msg.data + os.linesep
        self.statusTextCtrl.SetValue(newTextCtrl)
        
        
'''
class QuickResultsWindow(wx.Frame):
    """Displays quick results in new window"""
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(300,150), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        
        # Load icon       
        if hasattr(sys, 'frozen'):
            iconLoc = os.path.join(os.path.dirname(sys.executable),"SIMBA.exe")
            iconLoc = wx.IconLocation(iconLoc,0)
            self.SetIcon(wx.IconFromLocation(iconLoc))       
        
        # Looks for messages with these names and triggers event if found
        pub.subscribe(self.CreatePage, ("fileNames.key"))       
        pub.subscribe(self.PlugInValues, ("key.quickValues"))
        pub.subscribe(self.CloseWindow, ("quickValues.close"))
        
        panel = wx.Panel(self)
        self.notebook = wx.Notebook(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()
        #self.Fit()
        
        self.Show(True)
        

    def CreatePage(self, msg):
        """Creates tab with file name"""
        self.page = TabPanel(self.notebook)
        self.notebook.AddPage(self.page, msg.data)
        #self.GetParent().Layout()
    
    def PlugInValues(self,msg):
        """Inserts quick value data into corresponding tab"""
        data = msg.data
        compiledMessage = ""
        for index in data:
            value = repr(round(data[index], 3))
            compiledMessage += index + ": " + value + os.linesep
        
        self.page.quickData.SetValue(compiledMessage)
    
    def CloseWindow(self,msg):
        if msg.data == "Close":
            self.Close(True)
        

'''
##############################################################################

class NewParamsWindow(wx.Frame):
    """Displays window allowing user to make new parameters file"""
    def __init__(self, parent, title):
        wx.Frame.__init__(self,parent, title=title, size=(400,400), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX ^ wx.MINIMIZE_BOX)
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        self.Show(True)

class NewProjectWindow(wx.Frame):
    """Displays window allowing user to create a new project"""
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(400,400), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX ^ wx.MINIMIZE_BOX)
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        self.Show(True)
      
class Panel1(wx.Panel):
    """Holds all the main components (buttons, text boxes)"""
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        

        # Creates static text objects
        self.optionsText = wx.StaticText(self, wx.ID_ANY, "Options File: ",size=(100,25))
        self.folderText = wx.StaticText(self, wx.ID_ANY, "Output Folder: ",size=(100,25))        
        
        # Creates user form objects
        self.optionsControl = wx.TextCtrl(self, size = (300,-1))
        self.folderControl = wx.TextCtrl(self, size = (300,-1))
        
        # Creates buttons
        self.optionsExplorer = wx.Button(self, -1, "Browse")
        self.folderExplorer = wx.Button(self, -1, "Browse")
        self.runButton = wx.Button(self, -1, "Run Simulation")

        # Binds events to corresponding buttons
        self.optionsExplorer.Bind(wx.EVT_BUTTON, self.BrowseOptions)
        self.folderExplorer.Bind(wx.EVT_BUTTON, self.BrowseFolders)
        self.runButton.Bind(wx.EVT_BUTTON, self.RunSim)        
        
        # Create static box with along with it's sizer
        '''
        self.staticBox = wx.StaticBox(self, label = "Quick Options")
        self.boxSizerVert = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        self.boxSizerHori1 = wx.BoxSizer(wx.HORIZONTAL)
        self.boxSizerHori2 = wx.BoxSizer(wx.HORIZONTAL)        
        '''
        '''
        self.graphText = wx.StaticText(self, wx.ID_ANY, "Graphing program", size = (100,-1))
        self.graphControl = wx.TextCtrl(self, size = (200,-1))
        self.graphExplorer = wx.Button(self, -1, "Browse")
        self.graphExplorer.Bind(wx.EVT_BUTTON, self.BrowseUtilities)
        
        self.outputInputCheckBox = wx.CheckBox(self, name = "Output Input Parameters")
        self.outputInputText = wx.StaticText(self, wx.ID_ANY, "Transfer input parameters to output files")
        '''
        '''
        self.boxSizerHori1.Add(self.graphControl)
        self.boxSizerHori1.AddSpacer((10,-1))
        self.boxSizerHori1.Add(self.graphExplorer)
        
        self.boxSizerHori2.AddSizer((30,-1))
        self.boxSizerHori2.Add(self.outputInputCheckBox)
        self.boxSizerHori2.AddSpacer((5,-1))
        self.boxSizerHori2.Add(self.outputInputText)
        self.boxSizerVert.AddSpacer((-1,7))
        self.boxSizerVert.Add(self.graphText)
        self.boxSizerVert.Add(self.boxSizerHori1)
        self.boxSizerVert.AddSpacer((-1,10))
        self.boxSizerVert.Add(self.boxSizerHori2)
        '''

        # Create timer that triggers event 'OnTimer' every 100ms
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(100)        
        
        # Creates 3 horizontal sizers
        self.hSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hSizer3 = wx.BoxSizer(wx.HORIZONTAL)
        
        # Insert objects into row one with spacing
        self.hSizer1.AddSpacer((20,-1))
        self.hSizer1.Add(self.optionsText, 1)
        self.hSizer1.Add(self.optionsControl)
        self.hSizer1.AddSpacer((10,-1))
        self.hSizer1.Add(self.optionsExplorer)
        self.hSizer1.AddSpacer((20,-1))
        
        # Insert second row objects
        self.hSizer2.AddSpacer((20,-1))        
        self.hSizer2.Add(self.folderText, 1)
        self.hSizer2.Add(self.folderControl)
        self.hSizer2.AddSpacer((10,-1))
        self.hSizer2.Add(self.folderExplorer)
        self.hSizer2.AddSpacer((20,-1))
            
        # Insert third row objects
        self.hSizer3.AddSpacer((420,-1))
    
        # Create vertical sizer to lower 'Run Button'
        self.runVSizer = wx.BoxSizer(wx.VERTICAL)
        self.runVSizer.Add(self.runButton)
        
        # Insert sizer containing 'Run Button' into 3rd row
        self.hSizer3.Add(self.runVSizer)
        self.hSizer3.AddSpacer((20,-1))
        
        # Insert each row into vertical sizer to make 1 sizer
        self.vSizer = wx.BoxSizer(wx.VERTICAL)
        self.vSizer.AddSpacer((-1,20))
        self.vSizer.Add(self.hSizer1)
        self.vSizer.Add(self.hSizer2)
        self.vSizer.AddSpacer((-1,20))
        self.vSizer.Add(self.hSizer3)
        self.vSizer.AddSpacer((-1,20))
        
        
        # Layout sizers
        self.SetSizer(self.vSizer)
        self.SetAutoLayout(1)
        self.vSizer.Fit(self)

    
    def RunSim(self,e):
        """Runs the simulation and opens files if needed"""
        pub.sendMessage(("quickValues.close"), "Close")
        pub.sendMessage(("ClearTabs"), "True")
        options = self.optionsControl.GetValue()
        logging.debug("Entered path: %s", options)
        
        dictionary = FileToParams(options)
        
        
        # Sensitivity Analysis Function calls
        #percentChange = 15
        #senseAnalysis = AdjustParams(dictionary, percentChange)
        #senseAnalysisDict = sim.Simulation(senseAnalysis)
        dictionary = sim.Simulation(dictionary)
        
        outputDirectory = self.folderControl.GetValue()
        logging.debug("Entered out path: %s",outputDirectory)
        OutputFile(outputDirectory, dictionary)
        #OutputFile(outputDirectory, senseAnalysisDict)
        WriteFolder(options,outputDirectory)

        
        
        
        # Gather filenames and value for quick values
        fileNames = np.array(dictionary.keys())
        #fileNames = np.append(dictionary.keys(), senseAnalysisDict.keys())
        #resultsWindow = QuickResultsWindow(None, "Quick Results")
        
        for key in fileNames:
            msg = key
            pub.sendMessage(("fileNames.key"), msg)      
            
            if dictionary.has_key(key):
                currentDict = dictionary[key]
            #else:         # Used to make quick value tabs for senseAnalysis files
            #    currentDict = senseAnalysisDict[key]
            msg = currentDict
            pub.sendMessage(("fileName.data"), msg)
            quickValues = dict()
            

            paramHeaders = np.array(currentDict.keys())
            
            for x in range(len(paramHeaders)):
                currentValues = currentDict[paramHeaders[x]]
                if not np.ndim(currentValues) > 1:
                    quickValues[paramHeaders[x]] = currentValues
                    
            msg = quickValues
            pub.sendMessage(("key.quickValues"),msg)
            
            '''
            #Open files in graphing program if specified
            if len(self.graphControl.GetValue()) > 0:
                outFileLoc = os.path.join(outputDirectory, key)
                subprocess.Popen([self.graphFileLoc, outFileLoc])
            '''
            
        resultsWindow.Show()
        
        path = os.path.dirname(os.path.realpath("OPTIONS.csv"))
        path = os.path.join(path, "SimOutputMacro0904.xlsm")        
        
        excel = win32com.client.DispatchEx("Excel.Application")
        workbook = excel.workbooks.open(path)
        excel.run("ConsolidateData")
        excel.Visible = True
        workbook.Close(SaveChanges=1)
        excel.Quit
        
        resultsWindow.Freeze()
        '''
        try:
            os.startfile(path)
        except AttributeError:
            subprocess.call(['open', path])
        except:
            GUIdialog = wx.MessageDialog(None, "Error running macro. Please make sure SimOutputMacro is in the same folder as OPTIONS.csv.", "Error", wx.OK)
            GUIdialog.ShowModal()
            GUIdialog.Destroy()  
        '''
        
    
    
    def BrowseOptions(self,e):
        """ Browse for the options file """
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "Comma Seperated Value (.csv)|*.csv|Text file (.txt)|*.txt")
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.optionsControl.SetValue(os.path.join(self.dirname, self.filename))
            
            if os.path.exists(self.optionsControl.GetValue()) and self.folderControl.IsEmpty():
                try:
                    data = np.loadtxt(open(self.optionsControl.GetValue(), "rb"), dtype = 'string', delimiter=',')
                    self.folderControl.SetValue(data[1,3])
                    
                #Extracts all data from file into variable data
                except:
                    pass
                
        dlg.Destroy()
        
    def BrowseFolders(self,e):
        """ Browse for output folder """
        self.dirname = ''
        dlg = wx.DirDialog(self, "Choose a folder", self.dirname)
        if dlg.ShowModal() == wx.ID_OK:
            self.folderControl.SetValue(dlg.GetPath())
        dlg.Destroy()
        
    def BrowseUtilities(self,e):
        """ Browse for graphing program """
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a program", "", "", "Executable (.exe)|*.exe")
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.graphControl.SetValue(self.filename)
            self.graphFileLoc = os.path.join(self.dirname,self.filename)
            
            
        
    def OnTimer(self, e):
        """ Gray out Run Simulation when missing output or options file """
        if self.optionsControl.IsEmpty() or self.folderControl.IsEmpty():
            self.runButton.Enable(False)
        else:
            self.runButton.Enable(True)
        

            
        
        
class TabPanel(wx.Panel):
    """
    Generates panel for each tab
    """
    def __init__(self,parent):
        wx.Panel.__init__(self, parent= parent, id=wx.ID_ANY)
        
        
        self.quickData = wx.TextCtrl(self, wx.ID_ANY, "", style = wx.TE_READONLY | wx.TE_MULTILINE)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.quickData, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()
    
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

###############################################################################
# GUI Ends Here
###############################################################################
# Main loop and script starts here
###############################################################################

logging.basicConfig(filename="SIMBA_log.txt",format='%(asctime)s - %(levelname)s - %(message)s',level=logging.DEBUG)
logging.info("STARTING automation.py")


app = wx.App(False)
mainWindow = MainWindow(None, "SIMBA")
testWindow = MainFrame(None, "TEST")
#quickWindow = QuickResultsWindow(None, "Quick Results")

msg = datetime.now().strftime('%H:%M:%S') + ": " + "Welcome to SIMBA! Start by creating a new project or opening one that has already been generated"
pub.sendMessage(("AddStatus"), msg)  

app.MainLoop()

