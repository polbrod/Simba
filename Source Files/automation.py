# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 20:10:55 2013

@author: Sean
"""

import logging
import os
import numpy as np
import Simulation as sim
import wx

from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub

import sys, subprocess

def dependencies_for_automation():  #Missing imports needed to convert to .exe
    from scipy.sparse.csgraph import _validation

def FileToParams(inFiles):
    
    optionsFile = inFiles
    logging.info("STARTING FUNCTIONS FileToParams")
    os.chdir(os.path.dirname(os.path.realpath(inFiles)))    
    logging.debug("Options file location passed: %s", inFiles)
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
            GUIdialog = wx.MessageDialog(None, "Unable to load file in " + optionsFile +". Make sure "+ optionsFile + " is correct or specify a new options file", "Error", wx.OK)
            GUIdialog.ShowModal()
            GUIdialog.Destroy()
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
            GUIdialog = wx.MessageDialog(None, "Unable to save file to " + fileName +". Make sure "+ fileName + " is closed, specify a new file to save to, or pick a save directory that's writable.", "Error", wx.OK)
            GUIdialog.ShowModal()
            GUIdialog.Destroy()            
            raise Exception("Unable to save file")
            
        print("Data transfer to " + fileName + " complete")
        logging.info("Data converted and saved to %s", fileName)




##############################################################################
# GUI Starts Here
##############################################################################
class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800,800), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        
        # Load icon
        if hasattr(sys, 'frozen'):
            iconLoc = os.path.join(os.path.dirname(sys.executable),"BCS.exe")
            iconLoc = wx.IconLocation(iconLoc,0)
            self.SetIcon(wx.IconFromLocation(iconLoc))
        #else:
         #   iconLoc = os.path.join(os.path.dirname(__file__),__file__)

        
        # Setting up menu
        filemenu = wx.Menu()
        
        menuAbout = filemenu.Append(wx.ID_ABOUT, "About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT, "Exit"," Terminate the program")
        
        # Creating menubar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File") #Adds "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)

        # Set Events
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        self.MainPanel = wx.Panel(self,-1)
        self.Panel = Panel1(self)
        
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.Panel)
        
        self.MainPanel.SetSizer(self.mainSizer)
        #self.MainPanel.Fit()
        self.Fit()

        self.Show(True)

    def OnAbout(self,e) :
        dialogBox = wx.MessageDialog(self, "A simulation", "About BCS")
        dialogBox.ShowModal() # Show it
        dialogBox.Destroy() #Destroy it when finished
        
    def OnExit(self,e):
        logging.info("ENDING automation.py" + os.linesep + os.linesep)
        logging.shutdown()
        self.Close(True)
        
###############################################################################
        
class QuickResultsWindow(wx.Frame):
    """Displays quick results in new window"""
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(300,150), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        
        # Load icon       
        if hasattr(sys, 'frozen'):
            iconLoc = os.path.join(os.path.dirname(sys.executable),"BCS.exe")
            iconLoc = wx.IconLocation(iconLoc,0)
            self.SetIcon(wx.IconFromLocation(iconLoc))       
        
        # Looks for messages with these names and triggers event if found
        pub.subscribe(self.CreatePage, ("fileNames.key"))       
        pub.subscribe(self.PlugInValues, ("key.quickValues"))
        
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
        compiledMessage = os.linesep
        for index in data:
            compiledMessage += index + ": " + data[index] + os.linesep
        
        self.page.quickData.SetValue(compiledMessage)

##############################################################################
            
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
        self.staticBox = wx.StaticBox(self, label = "Optional: Graphing Utility")
        self.boxSizer = wx.StaticBoxSizer(self.staticBox, wx.HORIZONTAL)
        
        #self.graphText = wx.StaticText(self, wx.ID_ANY, "Graphing program: ", size = (100,25))
        self.graphControl = wx.TextCtrl(self, size = (200,-1))
        self.graphExplorer = wx.Button(self, -1, "Browse")
        self.graphExplorer.Bind(wx.EVT_BUTTON, self.BrowseUtilities)
        
        #self.boxSizer.Add(self.graphText, 1)
        self.boxSizer.Add(self.graphControl)
        self.boxSizer.AddSpacer((10,-1))
        self.boxSizer.Add(self.graphExplorer)
        

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
            
        # Insert optional program into 3rd row
        self.hSizer3.AddSpacer((20,-1))
        self.hSizer3.Add(self.boxSizer)
        self.hSizer3.AddSpacer((80,-1))
        
        # Create vertical sizer to lower 'Run Button'
        self.runVSizer = wx.BoxSizer(wx.VERTICAL)
        self.runVSizer.AddSpacer((-1,17))
        self.runVSizer.Add(self.runButton)
        
        # Insert sizer containing 'Run Button' into 3rd row
        self.hSizer3.Add(self.runVSizer)
        self.hSizer3.AddSpacer((20,-1))
        
        # Insert each row into vertical sizer to make 1 sizer
        self.vSizer = wx.BoxSizer(wx.VERTICAL)
        self.vSizer.AddSpacer((-1,20))
        self.vSizer.Add(self.hSizer1, 0, wx.EXPAND)
        self.vSizer.Add(self.hSizer2, 0, wx.EXPAND)
        self.vSizer.AddSpacer((-1,20))
        self.vSizer.Add(self.hSizer3, 0, wx.EXPAND)
        self.vSizer.AddSpacer((-1,20))
        
        
        # Layout sizers
        self.SetSizer(self.vSizer)
        self.SetAutoLayout(1)
        self.vSizer.Fit(self)

    
    def RunSim(self,e):
        """Runs the simulation and opens files if needed"""
        
        options = self.optionsControl.GetValue()
        logging.debug("Entered path: %s", options)
        
        dictionary = FileToParams(options)
        dictionary = sim.Simulation(dictionary)
        
        outputDirectory = self.folderControl.GetValue()
        logging.debug("Entered out path: %s",outputDirectory)
        OutputFile(outputDirectory, dictionary)
        
        # Gather filenames and value for quick values
        self.fileNames = np.array(dictionary.keys())
        resultsWindow = QuickResultsWindow(None, "Quick Results")
        
        for key in self.fileNames:
            msg = key
            pub.sendMessage(("fileNames.key"), msg)      
            
            currentDict = dictionary[key]
            quickValues = dict()
            paramHeaders = np.array(currentDict.keys())
            
            for x in range(len(paramHeaders)):
                currentValues = currentDict[paramHeaders[x]]
                if not np.ndim(currentValues) > 1:
                    quickValues[paramHeaders[x]] = currentValues
                    
            msg = quickValues
            pub.sendMessage(("key.quickValues"),msg)
            
            #Open files in graphing program if specified
            if len(self.graphControl.GetValue()) > 0:
                outFileLoc = os.path.join(outputDirectory, key)
                subprocess.Popen([self.graphFileLoc, outFileLoc])
                
        resultsWindow.Show()
        
            
    
    def BrowseOptions(self,e):
        """ Browse for the options file """
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "Comma Seperated Value (.csv)|*.csv|Text file (.txt)|*.txt")
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.optionsControl.SetValue(os.path.join(self.dirname, self.filename))
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
    


###############################################################################
# GUI Ends Here
###############################################################################
# Main loop and script starts here
###############################################################################

logging.basicConfig(filename="BCS_log.txt",format='%(asctime)s - %(levelname)s - %(message)s',level=logging.DEBUG)
logging.info("STARTING automation.py")



app = wx.App(False)
mainWindow = MainWindow(None, "Buckeye Current Simulation")
#quickWindow = QuickResultsWindow(None, "Quick Results")
app.MainLoop()

