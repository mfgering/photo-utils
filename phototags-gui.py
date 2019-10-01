import phototags
import logging, os, sys, threading, wx
import wx.grid as gridlib

class MainWindow(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, size=(600,400))
		self.target = None
		self.workerThread = None
		self.guiThreadId = threading.current_thread().ident
		self.logFrame = LogFrame(self)
		self.panel = wx.Panel(self, wx.ID_ANY)

		toolbar = self.CreateToolBar()

		self.startButton = wx.Button(toolbar, label="Start")
		toolbar.AddControl(self.startButton)
		self.startButton.Bind(wx.EVT_BUTTON, self.OnProcess)
		self.startButton.Disable()

		self.stopButton = wx.Button(toolbar, label="Stop")
		toolbar.AddControl(self.stopButton)
		self.stopButton.Bind(wx.EVT_BUTTON, self.OnStop)
		self.stopButton.Disable()

		self.showTagsButton = wx.Button(toolbar, label="Show Tags")
		toolbar.AddControl(self.showTagsButton)
		self.showTagsButton.Bind(wx.EVT_BUTTON, self.OnShowTags)
		self.showTagsButton.Disable()

		self.showBadTagsButton = wx.Button(toolbar, label="Show Bad Tags")
		toolbar.AddControl(self.showBadTagsButton)
		self.showBadTagsButton.Bind(wx.EVT_BUTTON, self.OnShowBadTags)
		self.showBadTagsButton.Disable()

		toolbar.Realize()

		#self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
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

		self.parseArgs()
		self.target = self.args.targ_arg

		self.tag_info = []
		self.setButtonStates()
		print("App starting")

	def parseArgs(self):
		parser = phototags.initArgParser()
		parser.add_argument('--target', dest='targ_arg', help="File or directory to check")
		self.args = parser.parse_args()

	def OnTarget(self,e):
		dlg = wx.DirDialog( self, message="Select a directory to process", name="target_picker")
		dlg.ShowModal()
		self.target = dlg.GetPath()
		self.args.target = self.target
		dlg.Destroy() # finally destroy it when finished.
		self.startButton.Enable()

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
		if os.path.isdir(self.target) or os.path.isfile(self.target):
			self.fileCount = 0
			self.filename = None
			self.tag_info = []
			self.StatusBar.SetStatusText("Starting to process images...")
			self.workerThread = PhotoTagsThread(self.processCallback, self.args, self.target)
			self.workerThread.start()
		else:
			self.StatusBar.SetStatusText("ERROR: Target '%s' is not a file or directory"%(self.target))
		self.setButtonStates()

	def OnStop(self, e):
		self.StatusBar.SetStatusText("Stopped")
		self.workerThread.stop()
		self.setButtonStates()

	def OnShowTags(self, e):
		font = wx.Font(18, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.BOLD)
		self.titleText = wx.StaticText(self.panel, label="Tags for Files", style=wx.ALIGN_CENTER)
		self.titleText.SetFont(font)
		titleSizer = wx.BoxSizer(wx.HORIZONTAL)
		titleSizer.Add(self.titleText, 1, wx.ALL|wx.EXPAND)
		self.grid = gridlib.Grid(self.panel)
		gridSizer = wx.BoxSizer(wx.HORIZONTAL)
		gridSizer.Add(self.grid, 1, wx.ALL|wx.EXPAND, 5)
		self.grid.CreateGrid(len(self.tag_info), 2)
		self.grid.SetDefaultCellOverflow(False)
		self.grid.SetColLabelValue(0, "Filename")
		self.grid.SetColLabelValue(1, "Tags")
		row_num = 0
		for row in self.tag_info:
			self.grid.SetCellValue(row_num, 0, row[0])
			self.grid.SetCellValue(row_num, 1, ", ".join(row[1]))
			attr = gridlib.GridCellAttr()
			attr.SetReadOnly(True)
			self.grid.SetRowAttr(row_num, attr)
			row_num += 1
		self.grid.AutoSize()
		panelSizer = wx.BoxSizer(wx.VERTICAL)
		panelSizer.Add(titleSizer, 0, wx.ALL|wx.EXPAND)
		panelSizer.Add(gridSizer, 0, wx.ALL|wx.EXPAND)
		self.panel.SetSizer(panelSizer)
		panelSizer.Fit(self)

	def OnShowBadTags(self, e):
		pass

	def setButtonStates(self):
		target_ok = os.path.isdir(self.target) or os.path.isfile(self.target)
		processing = self.workerThread is not None and not self.workerThread.stopping
		self.startButton.Enable(target_ok and not processing)
		self.stopButton.Enable(processing)
		showButtonsState = (not processing) and len(self.tag_info) > 0
		for button in [self.showTagsButton, self.showBadTagsButton]:
			button.Enable(showButtonsState)

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
			self.tag_info.append((self.filename, self.tags, self.missing_tags, self.bad_tags))
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
		pass #TODO: REMOVE THIS

	def showBadTags(self, filename, tags):
		pass #TODO: REMOVE THIS
	
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
	def __init__(self, callback, args, target):
		super().__init__()
		self.callback = callback
		self.errorCount = 0
		self.args = args
		self.target = target
		self.stopping = False

	def run(self):
		self.photo_tags = phototags.PhotoTags(target_required=False, callback=self.callback, args=self.args)
		if self.args.debug:
			self.photo_tags.logger.setLevel(logging.DEBUG)
		self.errorCount = self.photo_tags.process_target(self.target)

	def stop(self):
		self.photo_tags.stop_processing()
		self.stopping = True

app = wx.App(False)
frame = MainWindow(None, "Image Tag Checker")
app.MainLoop()