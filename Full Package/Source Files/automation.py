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
import  wx.lib.scrolledpanel as scrolled
import collections
import shutil

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
    
def ProjectToParams(inFiles):
    
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
        
    np.savetxt(optionsFile, data, delimiter=",", fmt="%s")
    logging.info("%s successfully edited", optionsFile)
    
    
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
         pub.sendMessage(("ProjectName"), self.projectName.GetValue())
         self.Destroy()
     def OnCancel(self, event):
         pub.sendMessage(("ProjectName"), "Cancel")
         self.Destroy()
          
     
class IOSplitterPanel(wx.Panel):
    """ Constructs a Vertical splitter window with left and right panels"""
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        splitter = wx.SplitterWindow(self, style = wx.SP_3D| wx.SP_LIVE_UPDATE)
        splitter.SetSashGravity(0.2)
        splitter.SetMinimumPaneSize(20)
        leftPanel = InputPanel(splitter, style = wx.BORDER_SIMPLE | wx.TAB_TRAVERSAL)
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
        pub.subscribe(self.SetCurrentFiles, ("InputFiles"))
        pub.subscribe(self.ChangeProjectName, ("ProjectName"))        
        pub.subscribe(self.DisableDeleteCopy, ("DisableDelete"))        

        
        self.currentFiles = np.empty(shape=(0,0))
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
        self.toolbar.AddControl(TransparentText(self.toolbar, wx.ID_ANY, " Parameter Filename  "))
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
        
        self.toolbar.AddControl(TransparentText(self.toolbar, wx.ID_ANY, " Output Directory  "))
        self.folderControl = wx.TextCtrl(self.toolbar, size = (300,-1))
        self.toolbar.AddControl(self.folderControl) 
        
        
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
            
            pub.sendMessage(("UpdateInput"), self.dictionary)
            
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Successfully created new project: " + newDirectory
            pub.sendMessage(("AddStatus"), msg)    
        

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
        pub.sendMessage(("UpdateInput"), self.dictionary)
        
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
            
            pub.sendMessage(("RemoveFiles"), True)
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
                pub.sendMessage(("AddStatus"), msg)  
                
            pub.sendMessage(("UpdateInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Opened project " + self.project
            pub.sendMessage(("AddStatus"), msg)    
              
            
            
        dlg.Destroy()
          
        
    
    def OnSave(self, e):
        """Saves the current parameter file open in input panel"""
        SaveInput(os.path.dirname(os.path.realpath(self.project)), self.currentFile)
        msg = datetime.now().strftime('%H:%M:%S') + ": " + "Successfully saved " + self.currentFile.keys()[0]
        pub.sendMessage(("AddStatus"), msg)  
        
        optionsData = np.loadtxt(open(self.project, "rb"), dtype = 'string', delimiter=',')
        if np.shape(optionsData)[0] > 1:
            optionsData[np.where(self.currentFiles == self.currentFile.keys()[0])[0][0]+1,2] = self.dictionary[self.currentFile.keys()[0]]["comments"][0]
            np.savetxt(self.project, optionsData, delimiter=",", fmt="%s")

        
    
    def OnSaveAll(self,e):
        """Saves all parameters file in the current project"""
        
        optionsData = np.loadtxt(open(self.project, "rb"), dtype = 'string', delimiter=',')
        
        for key in self.dictionary.keys():
            saveDict = dict()
            saveDict[key] = self.dictionary[key]
            SaveInput(os.path.dirname(os.path.realpath(self.project)), saveDict)

            if np.shape(optionsData)[0] > 1:
                optionsData[np.where(self.currentFiles == key)[0][0]+1,2] = self.dictionary[key]["comments"][0]
                             
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Successfully saved " + key
            pub.sendMessage(("AddStatus"), msg)  
            
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
            self.dictionary[self.newParamName.GetValue()]["wheel_radius"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["rolling_resistance"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["rider_mass"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["bike_mass"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["dist_to_speed_lookup"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["air_resistance"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["air_density"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["gravity"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["frontal_area"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["top_torque"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["top_rpm"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["max_distance_travel"] = np.array([""])
            self.dictionary[self.newParamName.GetValue()]["chain_efficiency"] = np.array([""])
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
             
            self.currentFiles = np.append(self.currentFiles, self.newParamName.GetValue())
            pub.sendMessage(("InputFiles"), self.currentFiles)
            pub.sendMessage(("ChangeSelection"), self.newParamName.GetValue())
            pub.sendMessage(("UpdateInput"), self.dictionary)
            
            if not os.path.exists(os.path.join(self.project, self.newParamName.GetValue())):
                self.OnSave(wx.EVT_ACTIVATE)                
                
        else:
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Must enter parameter filename before creating a new file"
            pub.sendMessage(("AddStatus"), msg)  
        pass
    
    def OnCopyParamFile(self, e):
        if len(self.newParamName.GetValue()) > 0:
            
            inFiles = np.loadtxt(open(self.project, "rb"), dtype = 'string', delimiter = ',')
            print "In Files"
            print inFiles
            print "Current File"
            print self.currentFile.keys()[0]
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
            pub.sendMessage(("InputFiles"), self.currentFiles)
            pub.sendMessage(("ChangeSelection"), self.newParamName.GetValue())
            pub.sendMessage(("UpdateInput"), self.dictionary)
             

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
            pub.sendMessage(("InputFiles"), self.currentFiles)
            pub.sendMessage(("ChangeSelection"), self.filename)
            pub.sendMessage(("UpdateInput"), self.dictionary)
            
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
        pub.sendMessage(("RemoveFiles"), keys)
        pub.sendMessage(("InputFiles"), keys)
        if len(keys) > 0:
            pub.sendMessage(("ChangeSelection"), keys[0])

        #pub.sendMessage(("InputFiles"), keys)
        self.dictionary = newDict
        pub.sendMessage(("UpdateInput"), newDict)
        


        

    
    def OnRun(self, e):
        """Runs the simulation and opens files if needed"""
        pub.sendMessage(("ClearTabs"), "True")
        logging.debug("Entered path: %s", self.project)
        
        dictionary = ProjectToParams(self.project)
        
        inFiles = np.loadtxt(open(self.project, "rb"), dtype = 'string', delimiter = ',')
        if not os.path.exists(self.folderControl.GetValue()):
            os.makedirs(self.folderControl.GetValue())
        
        inFiles[1,3] = self.folderControl.GetValue()
        # Sensitivity Analysis Function calls
        #percentChange = 15
        #senseAnalysis = AdjustParams(dictionary, percentChange)
        #senseAnalysisDict = sim.Simulation(senseAnalysis)
        outputDict = sim.Simulation(deepcopy(dictionary))
        
        outputDirectory = self.folderControl.GetValue()
        logging.debug("Entered out path: %s",outputDirectory)
        OutputFile(outputDirectory, outputDict)
        #OutputFile(outputDirectory, senseAnalysisDict)
        WriteFolder(self.project,outputDirectory)
        
        # Gather filenames and value for quick values
        fileNames = np.array(outputDict.keys())
        #fileNames = np.append(outputDict.keys(), senseAnalysisDict.keys())
        #resultsWindow = QuickResultsWindow(None, "Quick Results")
        index = 1
        for key in fileNames:
            inFiles[index, 2] = dictionary[key]["comments"][0]
            msg = key
            pub.sendMessage(("fileNames.key"), msg)      
            
            if outputDict.has_key(key):
                currentDict = outputDict[key]
            #else:         # Used to make quick value tabs for senseAnalysis files
            #    currentDict = senseAnalysisDict[key]
            msg = currentDict
            pub.sendMessage(("fileName.data"), msg)         
            index = index + 1
        
  
        np.savetxt(self.project, inFiles, delimiter=",", fmt="%s")
        path = os.path.dirname(os.path.realpath("OPTIONS.csv"))
        
        
        path = os.path.join(path, "SimOutputMacro1013.xlsm")        
        
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
        
        
        self.toolbar = wx.ToolBar(self, wx.ID_ANY, size = (2000, 32))
        self.toolbar.SetToolBitmapSize( ( 21, 21 ) )
        self.dropDownList = wx.ComboBox(self.toolbar, -1, style = wx.CB_READONLY|wx.TRANSPARENT_WINDOW)
        self.Bind(wx.EVT_COMBOBOX, self.UpdateFields)
        self.toolbar.AddControl(TransparentText(self.toolbar, wx.ID_ANY, "      Parameter File     "))
        self.toolbar.AddControl(self.dropDownList)

                
        self.values=[]
        self.keys=[]
        
        
        #Create Sizers    
        self.vSizer = wx.BoxSizer(wx.VERTICAL)
        self.hSizer= wx.BoxSizer(wx.HORIZONTAL)
        self.vSizer1 = wx.BoxSizer(wx.VERTICAL)
        
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Gearing (ratio)" ,size=(180,25)))        
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Distance to Altitude Lookup",size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Step (seconds)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Total Time (seconds)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Wheel Radius (meters)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Rolling Resistance" ,size=(180,25)))      
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Rider Mass (kg)",size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Bike Mass (kg)",size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Distance to Speed Lookup",size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Air Resistance" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Air Density (kg/m^2)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Gravity (m/s^2)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Frontal Area (m^2)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Top Torque (Nm)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Top RPM (RPM)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Max Distance Travel (meters)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Chain Efficiency" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Battery Efficiency" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Motor Torque Constant (Nm/amps rms)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Motor RPM Constant (RPM/Voltage)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Motor Controller Efficiency Lookup" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Motor Efficiency Lookup" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Motor Top Power (watts)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Battery Max Current (I)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Max Amphours (Amphours)" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Cell Amount in Series" ,size=(180,25)))
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Soc To Voltage Lookup" ,size=(180,25)))
        self.vSizer1.AddSpacer(3)
        self.vSizer1.Add(wx.StaticText(self, wx.ID_ANY, "Comments", size=(180,25)))
 
        
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
        self.p16 = wx.TextCtrl(self, size=(150,25))
        self.p17 = wx.TextCtrl(self, size=(150,25))
        self.p18 = wx.TextCtrl(self, size=(150,25))
        self.p20 = wx.TextCtrl(self, size=(150,25))
        self.p21 = wx.TextCtrl(self, size=(150,25))
        self.p22 = wx.TextCtrl(self, size=(150,25))
        self.p23 = wx.TextCtrl(self, size=(150,25))
        self.p24 = wx.TextCtrl(self, size=(150,25))
        self.p25 = wx.TextCtrl(self, size=(150,25))
        self.p26 = wx.TextCtrl(self, size=(150,25))
        self.p27 = wx.TextCtrl(self, size=(150,25))
        self.p28 = wx.TextCtrl(self, size=(150,25))
        self.comments = wx.TextCtrl(self, size = (355,160), style = wx.TE_MULTILINE)
        
        self.textCtrlList = (self.p0, self.p1, self.p2, self.p3, self.p4, self.p5,
                        self.p6, self.p7, self.p8, self.p9, self.p10, self.p11,
                        self.p12, self.p13, self.p14, self.p16,
                        self.p17, self.p18, self.p20, self.p21,
                        self.p22, self.p23, self.p24, self.p25, self.p26,
                        self.p27, self.p28, self.comments)
        
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
        self.p16.Bind(wx.EVT_TEXT, self.UpdateP16)
        self.p17.Bind(wx.EVT_TEXT, self.UpdateP17)
        self.p18.Bind(wx.EVT_TEXT, self.UpdateP18)
        self.p20.Bind(wx.EVT_TEXT, self.UpdateP20)
        self.p21.Bind(wx.EVT_TEXT, self.UpdateP21)
        self.p22.Bind(wx.EVT_TEXT, self.UpdateP22)
        self.p23.Bind(wx.EVT_TEXT, self.UpdateP23)
        self.p24.Bind(wx.EVT_TEXT, self.UpdateP24)
        self.p25.Bind(wx.EVT_TEXT, self.UpdateP25)
        self.p26.Bind(wx.EVT_TEXT, self.UpdateP26)
        self.p27.Bind(wx.EVT_TEXT, self.UpdateP27)
        self.p28.Bind(wx.EVT_TEXT, self.UpdateP28)
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
        self.vSizer.Add(self.toolbar)
        self.vSizer.AddSpacer((-1,10))        
        
        #self.vSizer.Add(self.buttonRun)

        self.vSizer.Add(self.hSizer)
        self.vSizer.Add(self.commentsSizer)
        
        self.SetSizer(self.vSizer)
        
        self.toolbar.Realize()
        self.SetAutoLayout(1)
        self.vSizer.Fit(self)
        self.Layout()
        self.SetAutoLayout(1)
        self.SetupScrolling(scroll_x = False, scroll_y = True, rate_x=20, rate_y=20, scrollToTop=True)
    
        
    
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
        self
        index = 0
        for file in self.dictionary:   
            self.fileToFile[self.fileNames[index]] = file 
            index = index + 1
          
        self.fileToFile
        if len(self.dictionary) > 0:
            
            self.UpdateFields(wx.EVT_COMBOBOX)
            pub.sendMessage(("DisableDelete"), False)
            #pub.sendMessage(("DictFromInput"), self.dictionary)

        else:
            for i in xrange(len(self.textCtrlList)):
                self.textCtrlList[i].SetValue("")            
            
            self.dropDownList.Clear()
            pub.sendMessage(("DisableDelete"), True)
            


        
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
        currentFile = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]
        fileDict = dict()
        fileDict[self.fileToFile[self.dropDownList.GetValue()]] = currentFile
        pub.sendMessage(("CurrentFile"), fileDict)
        
        
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
            self.p1.ChangeValue(str(currentFile["dist_to_alt_lookup"][0]))
        except:
            self.p1.ChangeValue('')
        try:
            self.p2.ChangeValue(str(currentFile["step"][0]))   
        except:
            self.p2.ChangeValue('')
        try:
            self.p3.ChangeValue(str(currentFile["total_time"][0]))
        except:
            self.p3.ChangeValue('')
        try:
            self.p4.ChangeValue(str(currentFile["wheel_radius"][0]))   
        except:
            self.p4.ChangeValue('')
        try:
            self.p5.ChangeValue(str(currentFile["rolling_resistance"][0]))
        except:
            self.p5.ChangeValue('')
        try:
            self.p6.ChangeValue(str(currentFile["rider_mass"][0]))      
        except:
            self.p6.ChangeValue('')
        try:
            self.p7.ChangeValue(str(currentFile["bike_mass"][0]))
        except:
            self.p7.ChangeValue('')
        try:
            self.p8.ChangeValue(str(currentFile["dist_to_speed_lookup"][0]))  
        except:
            self.p8.ChangeValue('')
        try:
            self.p9.ChangeValue(str(currentFile["air_resistance"][0]))
        except:
            self.p9.ChangeValue('')
        try:
            self.p10.ChangeValue(str(currentFile["air_density"][0]))  
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
            self.p13.ChangeValue(str(currentFile["top_torque"][0]))
        except:
            self.p13.ChangeValue('')
        try:
            self.p14.ChangeValue(str(currentFile["top_rpm"][0]))  
        except:
            self.p14.ChangeValue('')
        try:
            self.p16.ChangeValue(str(currentFile["max_distance_travel"][0]))
        except:
            self.p16.ChangeValue('')
        try:
            self.p17.ChangeValue(str(currentFile["chain_efficiency"][0]))
        except:
            self.p17.ChangeValue('')
        try:
            self.p18.ChangeValue(str(currentFile["battery_efficiency"][0])) 
        except:
            self.p18.ChangeValue('')
        try:
            self.p20.ChangeValue(str(currentFile["motor_torque_constant"][0]))
        except:
            self.p20.ChangeValue('')
        try:
            self.p21.ChangeValue(str(currentFile["motor_rpm_constant"][0]))    
        except:
            self.p21.ChangeValue('')
        try:
            self.p22.ChangeValue(str(currentFile["motor_controller_eff_lookup"][0]))
        except:
            self.p22.ChangeValue('')
        try:
            self.p23.ChangeValue(str(currentFile["motor_eff_lookup"][0]))
        except:
            self.p23.ChangeValue('')
        try:
            self.p24.ChangeValue(str(currentFile["motor_top_power"][0]))
        except:
            self.p24.ChangeValue('')
        try:
            self.p25.ChangeValue(str(currentFile["batt_max_current"][0]))
        except:
            self.p25.ChangeValue('')
        try:
            self.p26.ChangeValue(str(currentFile["max_amphour"][0]))
        except:
            self.p26.ChangeValue('')
        try:
            self.p27.ChangeValue(str(currentFile["series_cells"][0]))
        except:
            self.p27.ChangeValue('')
        try:
            self.p28.ChangeValue(str(currentFile["soc_to_voltage_lookup"][0]))
        except:
            self.p28.ChangeValue('')
        try:
            self.comments.ChangeValue(str(currentFile["comments"][0]))
        except:
            self.comments.ChangeValue('')

    
    def UpdateP0 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['gearing'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['gearing'] = [self.p0.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Gearing changed from " + str(previousValue) + " to " + self.p0.GetValue()
            pub.sendMessage(("AddStatus"), msg)  
        except:
            pass
        
    def UpdateP1 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['dist_to_alt_lookup'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['dist_to_alt_lookup'] = [self.p1.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Distance to Altitude Lookup changed from " + str(previousValue) + " to " + self.p1.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP2 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['step'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['step'] = [self.p2.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Step changed from " + str(previousValue) + " to " + self.p2.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP3 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['total_time'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['total_time'] = [self.p3.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Total Time changed from " + str(previousValue) + " to " + self.p3.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP4 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['wheel_radius'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['wheel_radius'] = [self.p4.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Wheel Radius changed from " + str(previousValue) + " to " + str(self.p4.GetValue())
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP5 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['rolling_resistance'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['rolling_resistance'] = [self.p5.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Rolling Resistance changed from " + str(previousValue) + " to " + str(self.p5.GetValue())
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP6 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['rider_mass'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['rider_mass'] = [self.p6.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Rider Mass changed from " + str(previousValue) + " to " + str(self.p6.GetValue())
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP7 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['bike_mass'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['bike_mass'] = [self.p7.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Bike mass changed from " + str(previousValue) + " to " + self.p7.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP8 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['dist_to_speed_lookup'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['dist_to_speed_lookup'] = [self.p8.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Distance to Speed Lookup changed from " + str(previousValue) + " to " + self.p8.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP9 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['air_resistance'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['air_resistance'] = [self.p9.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Air Resistance changed from " + str(previousValue) + " to " + self.p9.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP10 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['air_density'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['air_density'] = [self.p10.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Air Density changed from " + str(previousValue) + " to " + self.p10.GetValue()
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
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['top_torque'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['top_torque'] = [self.p13.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Top Torque changed from " + str(previousValue) + " to " + self.p13.GetValue()
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
        
        
    def UpdateP16 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['max_distance_travel'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['max_distance_travel'] = [self.p16.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Max Distance Travel changed from " + str(previousValue) + " to " + self.p16.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP17 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['chain_efficiency'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['chain_efficiency'] = [self.p17.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Chain Efficiency changed from " + str(previousValue) + " to " + self.p17.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP18 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['battery_efficiency'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['battery_efficiency'] = [self.p18.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Battery Efficiency changed from " + str(previousValue) + " to " + self.p18.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP20 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_torque_constant'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_torque_constant'] = [self.p20.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Motor Torque Constant changed from " + str(previousValue) + " to " + self.p20.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP21 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_rpm_constant'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_rpm_constant'] = [self.p21.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Motor RPM Constant changed from " + str(previousValue) + " to " + self.p21.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP22 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_controller_eff_lookup'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_controller_eff_lookup'] = [self.p22.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Motor Controller Efficiency Lookup changed from " + str(previousValue) + " to " + self.p22.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP23 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_eff_lookup'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_eff_lookup'] = [self.p23.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Motor Efficiency Lookup changed from " + str(previousValue) + " to " + self.p23.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
        
    def UpdateP24 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_top_power'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['motor_top_power'] = [self.p24.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Motor Top Power changed from " + str(previousValue) + " to " + self.p24.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
        
    def UpdateP25 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['batt_max_current'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['batt_max_current'] = [self.p25.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Battery Max Current changed from " + str(previousValue) + " to " + self.p25.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass
    
    def UpdateP26 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['max_amphour'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['max_amphour'] = [self.p26.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Max Amphours changed from " + str(previousValue) + " to " + self.p26.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass

    def UpdateP27 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['series_cells'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['series_cells'] = [self.p27.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Cell Amount in Series changed from " + str(previousValue) + " to " + self.p27.GetValue()
            pub.sendMessage(("AddStatus"), msg)
        except:
            pass    

    def UpdateP28 (self, e):
        try:
            previousValue = self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['soc_to_voltage_lookup'][0]
            self.dictionary[self.fileToFile[self.dropDownList.GetValue()]]['soc_to_voltage_lookup'] = [self.p28.GetValue()]
            pub.sendMessage(("DictFromInput"), self.dictionary)
            msg = datetime.now().strftime('%H:%M:%S') + ": " + "Soc to Voltage Lookup changed from " + str(previousValue) + " to " + self.p28.GetValue()
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
        self.statusTextCtrl.ShowPosition(self.statusTextCtrl.GetLastPosition())
        
##############################################################################        
        
class TransparentText(wx.StaticText):
    def __init__(self, parent, id=wx.ID_ANY, label='', pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TRANSPARENT_WINDOW, name='transparenttext'):
        wx.StaticText.__init__(self, parent, id, label, pos, size, style, name)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_paint(self, event):
        bdc = wx.PaintDC(self)
        dc = wx.GCDC(bdc)

        font_face = self.GetFont()
        font_color = self.GetForegroundColour()

        dc.SetFont(font_face)
        dc.SetTextForeground(font_color)
        dc.DrawText(self.GetLabel(), 0, 0)

    def on_size(self, event):
        self.Refresh()
        event.Skip()

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

###############################################################################
# GUI Ends Here
###############################################################################
# Main loop and script starts here
###############################################################################

logging.basicConfig(filename="SIMBA_log.txt",format='%(asctime)s - %(levelname)s - %(message)s',level=logging.DEBUG)
logging.info("STARTING automation.py")


app = wx.App(False)
testWindow = MainFrame(None, "SIMBA")
#quickWindow = QuickResultsWindow(None, "Quick Results")

msg = datetime.now().strftime('%H:%M:%S') + ": " + "Welcome to SIMBA! Start by creating a new project or opening one that has already been generated"
pub.sendMessage(("AddStatus"), msg)  

app.MainLoop()

