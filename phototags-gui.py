import phototags
import logging, sys, threading, wx

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(600,400))
        self.target = None
        self.guiThreadId = threading.current_thread().ident
        self.logFrame = LogFrame(self)

        self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.CreateStatusBar()

        filemenu=wx.Menu()
        target_id = wx.Window.NewControlId()
        menuTarget = filemenu.Append(target_id, "&Target", "Target directory or file to process")
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        processMenu = wx.Menu()
        processId = wx.Window.NewControlId()
        menuProcess = processMenu.Append(processId, "&Start", "Start processing the target directory")
        stopId = wx.Window.NewControlId()
        menuStop = processMenu.Append(stopId, "S&top", "Stop processing the target directory")

        helpMenu = wx.Menu()
        logId = wx.Window.NewControlId()
        menuLog = helpMenu.Append(logId, "&Log", "Show log records")

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(processMenu,"&Process")
        menuBar.Append(helpMenu, "&Help")
    
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Set events.
        self.Bind(wx.EVT_MENU, self.OnTarget, menuTarget)
        self.Bind(wx.EVT_MENU, self.OnProcess, menuProcess)
        self.Bind(wx.EVT_MENU, self.OnStop, menuStop)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnLog, menuLog)
        self.Show(True)
        print("App starting")


    def OnTarget(self,e):
        dlg = wx.DirDialog( self, message="Select a directory to process", name="target_picker")
        dlg.ShowModal()
        self.target = dlg.GetPath()
        dlg.Destroy() # finally destroy it when finished.

    def OnAbout(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog(self, "Process image tags", "About phototags-gui", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnLog(self,e):
        if self.logFrame is None:
            self.logFrame = LogFrame(self)
        self.logFrame.Show()

    def logClosed(self):
        self.logFrame = None

    def OnProcess(self, e):
        self.fileCount = 0
        self.filename = None
        self.StatusBar.SetStatusText("Starting to process images...")
        self.workerThread = PhotoTagsThread(self.processCallback)
        self.workerThread.start()

    def OnStop(self, e):
        self.StatusBar.SetStatusText("Stopped")
        self.workerThread.stop()

    def processCallback(self, callbackName, callbackData):
        if callbackName == "tags":
            self.fileCount += 1
            self.filename = callbackData["filename"]
            self.tags = callbackData["tags"]
            self.missing_tags = callbackData["missingTags"]
            if len(self.missing_tags) > 0:
                self.showMissingTags(self.filename, self.missing_tags)
            self.bad_tags = callbackData["badTags"]
            if len(self.bad_tags) > 0:
                self.showBadTags(self.filename, self.bad_tags)

            self.StatusBar.SetStatusText("%s: %s: %s" % (self.fileCount, self.filename, ", ".join(self.tags)))
        elif callbackName == "done":
            self.errorCount = callbackData["errorCount"]
            status = "Done"
            if callbackData["wasStopped"]:
                status = "Stopped"
            self.StatusBar.SetStatusText("Files: %s; %s - total errors: %s" % (self.fileCount, status, self.errorCount))
        else:
            logging.getLogger().error("Unknown callback name %s", callbackName)
            self.StatusBar.SetStatusText("Error: Unknown callback name %s" % (callbackName))

    def showMissingTags(self, filename, tags):
        pass

    def showBadTags(self, filename, tags):
        pass
    
    def OnExit(self,e):
        self.Close(True)  # Close the frame.

class LogFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY, "Image Tags Log")
 
        # Add a panel so it looks the correct on all platforms
        panel = wx.Panel(self, wx.ID_ANY)
        log = wx.TextCtrl(panel, wx.ID_ANY, size=(300,100),
                          style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        btn = wx.Button(panel, wx.ID_ANY, 'Push me!')
        self.Bind(wx.EVT_BUTTON, self.onButton, btn)
 
        # Add widgets to a sizer        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(log, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)
        panel.SetSizer(sizer)
 
        # redirect text here
        redir=RedirectText(log, threading.current_thread().ident)
        sys.stdout = redir
        sys.stderr = redir

        self.Bind(wx.EVT_CLOSE, self.OnLogClose)
 
    def onButton(self, event):
        self.GetParent().onProcess(event) 
        #print("You pressed the button!")

    def OnLogClose(self,e):
        self.GetParent().logClosed()
        self.Destroy()
    

class RedirectText(object):
    def __init__(self, aWxTextCtrl, guiThreadId):
        self.out=aWxTextCtrl
        self.guiThreadId = guiThreadId

    def write(self, string):
        threadId = threading.current_thread().ident
        if self.guiThreadId == threadId:
            self.out.WriteText(string)
        else:
            wx.CallAfter(self.out.WriteText, string)

class PhotoTagsThread(threading.Thread):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.errorCount = 0

    def run(self):
        self.photo_tags = phototags.PhotoTags(target_required=False, callback=self.callback)
        self.photo_tags.logger.setLevel(logging.DEBUG)
        self.errorCount = self.photo_tags.process_target()

    def stop(self):
        self.photo_tags.stop_processing()

app = wx.App(False)
frame = MainWindow(None, "Image Tag Checker")
app.MainLoop()