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
            GUIbox = wx.MessageDialog(None, "Unable to load file in " + optionsFile +". Make sure "+ optionsFile + " is correct or specify a new options file", "Error", wx.OK)
            GUIbox.ShowModal()
            GUIbox.Destroy()
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
        fileName = folderName + "/" + key
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
            raise Exception("Unable to save file")
            
        print("Data transfer to " + fileName + " complete")
        logging.info("Data converted and saved to %s", fileName)


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800,800), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        
        #self.CreateStatusBar()
        
        # Setting up menu
        filemenu = wx.Menu()
        
        menuOpen = filemenu.Append(wx.ID_OPEN, "Open", "Open a file")
        menuAbout = filemenu.Append(wx.ID_ABOUT, "About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT, "Exit"," Terminate the program")
        
        # Creating menubar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File") #Adds "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)

        # Set Events
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        
        self.Panel = Panel1(self)
        self.Fit()

        self.Show(True)

    def OnAbout(self,e) :
        dialogBox = wx.MessageDialog(self, "A simulation", "About Buckeye Current Simulation")
        dialogBox.ShowModal() # Show it
        dialogBox.Destroy() #Destroy it when finished
        
    def OnExit(self,e):
        logging.info("ENDING automation.py" + os.linesep + os.linesep)
        logging.shutdown()
        self.Close(True)
        
        
    def OnOpen(self,e):
        """ Open a file """
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "Comma Seperated Value (.csv)|*.csv|Text file (.txt)|*.txt")
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.control.SetValue(os.path.join(self.dirname, self.filename))
        dlg.Destroy()
        
    
        
class Panel1(wx.Panel):
    """Holds all the components (buttons, text boxes)"""
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        

        
        self.optionsText = wx.StaticText(self, wx.ID_ANY, "Options File: ",size=(100,25))
        self.folderText = wx.StaticText(self, wx.ID_ANY, "Output Folder: ",size=(100,25))        
        
        self.optionsControl = wx.TextCtrl(self, size = (250,-1))
        self.folderControl = wx.TextCtrl(self, size = (250,-1))
        
        self.optionsExplorer = wx.Button(self, -1, "Browse")
        self.folderExplorer = wx.Button(self, -1, "Browse")
        self.runButton = wx.Button(self, -1, "Run Simulation")

        
        self.optionsExplorer.Bind(wx.EVT_BUTTON, self.BrowseOptions)
        self.folderExplorer.Bind(wx.EVT_BUTTON, self.BrowseFolders)
        self.runButton.Bind(wx.EVT_BUTTON, self.RunSim)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(100)        
        
        self.hSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hSizer3 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.hSizer1.AddSpacer((50,-1))
        self.hSizer1.Add(self.optionsText, 1)
        self.hSizer1.Add(self.optionsControl)
        self.hSizer1.AddSpacer((10,-1))
        self.hSizer1.Add(self.optionsExplorer)
        self.hSizer1.AddSpacer((20,-1))

        self.hSizer2.AddSpacer((50,-1))        
        self.hSizer2.Add(self.folderText, 1)
        self.hSizer2.Add(self.folderControl)
        self.hSizer2.AddSpacer((10,-1))
        self.hSizer2.Add(self.folderExplorer)
        self.hSizer2.AddSpacer((20,-1))
            
        self.hSizer3.AddSpacer((400,-1))
        self.hSizer3.Add(self.runButton)
        self.hSizer3.AddSpacer((20,-1))
        # Use some sizers to see layout options
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
        options = self.optionsControl.GetValue()
        logging.debug("Entered path: %s", options)
        dictionary = FileToParams(options)
        dictionary = sim.Simulation(dictionary)
        outputDirectory = self.folderControl.GetValue()
        logging.debug("Entered out path: %s",outputDirectory)
        OutputFile(outputDirectory, dictionary)
    
    def BrowseOptions(self,e):
        """ Open a file """
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "Comma Seperated Value (.csv)|*.csv|Text file (.txt)|*.txt")
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.optionsControl.SetValue(os.path.join(self.dirname, self.filename))
        dlg.Destroy()
        
    def BrowseFolders(self,e):
        """ Open a folder """
        self.dirname = ''
        dlg = wx.DirDialog(self, "Choose a folder", self.dirname)
        if dlg.ShowModal() == wx.ID_OK:
            self.folderControl.SetValue(dlg.GetPath())
        dlg.Destroy()
        
    def OnTimer(self, e):
        if self.optionsControl.IsEmpty() or self.folderControl.IsEmpty():
            self.runButton.Enable(False)
        else:
            self.runButton.Enable(True)
            
print
print
print

logging.basicConfig(filename="BCS_log.txt",format='%(asctime)s - %(levelname)s - %(message)s',level=logging.DEBUG)
#
logging.info("STARTING automation.py")


app = wx.App(False)
mainWindow = MainWindow(None, "Buckeye Current Simulation")
app.MainLoop()



'''

while True: #Make sure user input points to a file
    try:
        options = raw_input("Enter full path to options file: ")

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

'''

