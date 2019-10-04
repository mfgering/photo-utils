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
		self.tagsFrame = None
		self.panel = wx.Panel(self, wx.ID_ANY)
		panelSizer = wx.BoxSizer(wx.VERTICAL)
		self.panel.SetSizer(panelSizer)
		self.grid = None
		self.titleText = None

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

		self.showMissingTagsButton = wx.Button(toolbar, label="Show Missing Tags")
		toolbar.AddControl(self.showMissingTagsButton)
		self.showMissingTagsButton.Bind(wx.EVT_BUTTON, self.OnShowMissingTags)
		self.showMissingTagsButton.Disable()

		toolbar.Realize()
		self.CreateStatusBar()

		filemenu=wx.Menu()
		target_id = wx.Window.NewControlId()
		menuTarget = filemenu.Append(target_id, "&Target", "Target directory or file to process")
		menuTags = filemenu.Append(wx.ID_ANY, "Tags", "Tag configuration")
		menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

		processMenu = wx.Menu()
		processId = wx.Window.NewControlId()
		menuProcess = processMenu.Append(processId, "&Start", "Start processing the target directory")
		stopId = wx.Window.NewControlId()
		menuStop = processMenu.Append(stopId, "S&top", "Stop processing the target directory")

		helpMenu = wx.Menu()
		logId = wx.Window.NewControlId()
		menuLog = helpMenu.Append(logId, "&Log", "Show log records")
		menuAbout = helpMenu.Append(wx.ID_ABOUT, "&About"," Information about this program")

		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
		menuBar.Append(processMenu,"&Process")
		menuBar.Append(helpMenu, "&Help")
	
		self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

		# Set events.
		self.Bind(wx.EVT_MENU, self.OnTarget, menuTarget)
		self.Bind(wx.EVT_MENU, self.OnTags, menuTags)
		self.Bind(wx.EVT_MENU, self.OnProcess, menuProcess)
		self.Bind(wx.EVT_MENU, self.OnStop, menuStop)
		self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
		self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
		self.Bind(wx.EVT_MENU, self.OnLog, menuLog)
		self.Show(True)
		try:
			self.parseArgs()
			self.target = self.args.targ_arg

			self.config = phototags.PhotoTagsConfig()
			self.config.read_config(self.args.config)

			self.tag_info = []
			self.setButtonStates()
		except Exception as exc:
			self.GetStatusBar().SetStatusText("Error: "+str(exc))
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

	def OnTags(self, e):
		if self.tagsFrame is None:
			self.tagsFrame = TagsFrame(self, self.config)
		self.tagsFrame.Show()

	def OnAbout(self,e):
		# A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
		dlg = wx.MessageDialog(self, "Process image tags", "About phototags-gui", wx.OK)
		dlg.ShowModal() # Show it
		dlg.Destroy() # finally destroy it when finished.

	def OnLog(self, e):
		if self.logFrame is None:
			self.logFrame = LogFrame(self)
		self.logFrame.Show()

	def logClosed(self):
		self.logFrame = None

	def tagsClosed(self):
		self.tagsFrame = None

	def resetResults(self):
		if self.grid is not None:
			self.grid.Destroy()
			self.grid = None
		if self.titleText is not None:
			self.titleText.Destroy()
			self.titleText = None

	def OnProcess(self, e):
		if os.path.isdir(self.target) or os.path.isfile(self.target):
			self.fileCount = 0
			self.filename = None
			self.tag_info = []
			self.StatusBar.SetStatusText("Starting to process images...")
			self.resetResults()
			self.workerThread = PhotoTagsThread(self.processCallback, self.args, self.target, self.config)
			self.workerThread.start()
		else:
			self.StatusBar.SetStatusText("ERROR: Target '%s' is not a file or directory"%(self.target))
		self.setButtonStates()

	def OnStop(self, e):
		self.StatusBar.SetStatusText("Stopped")
		self.workerThread.stop()
		self.setButtonStates()

	def OnShowTags(self, e):
		self.resetResults()
		self.setResultsTitle("File Tags")
		self.grid = gridlib.Grid(self.panel)
		gridSizer = wx.BoxSizer(wx.HORIZONTAL)
		gridSizer.Add(self.grid, 1, wx.ALL|wx.EXPAND, 5)
		self.panel.GetSizer().Add(gridSizer, 0, wx.ALL|wx.EXPAND)
		self.grid.CreateGrid(len(self.tag_info), 2)
		self.grid.SetDefaultCellOverflow(False)
		self.grid.SetColLabelValue(0, "Filename")
		self.grid.SetColLabelValue(1, "All Tags")
		row_num = 0
		for row in self.tag_info:
			self.grid.SetCellValue(row_num, 0, row[0])
			self.grid.SetCellValue(row_num, 1, ", ".join(row[1]))
			attr = gridlib.GridCellAttr()
			attr.SetReadOnly(True)
			self.grid.SetRowAttr(row_num, attr)
			row_num += 1
		self.grid.AutoSize()
		self.panel.Layout()

	def OnShowBadTags(self, e):
		self.resetResults()
		self.setResultsTitle("Bad Tags")
		rows = [ (r[0], r[3]) for r in self.tag_info if len(r[3]) > 0]
		self.grid = gridlib.Grid(self.panel)
		gridSizer = wx.BoxSizer(wx.HORIZONTAL)
		gridSizer.Add(self.grid, 1, wx.ALL|wx.EXPAND, 5)
		self.panel.GetSizer().Add(gridSizer, 0, wx.ALL|wx.EXPAND)
		self.grid.CreateGrid(len(rows), 2)
		self.grid.SetDefaultCellOverflow(False)
		self.grid.SetColLabelValue(0, "Filename")
		self.grid.SetColLabelValue(1, "Bad Tags")
		row_num = 0
		for row in rows:
			self.grid.SetCellValue(row_num, 0, row[0])
			self.grid.SetCellValue(row_num, 1, ", ".join(row[1]))
			attr = gridlib.GridCellAttr()
			attr.SetReadOnly(True)
			self.grid.SetRowAttr(row_num, attr)
			row_num += 1
		self.grid.AutoSize()
		self.panel.Layout()

	def OnShowMissingTags(self, e):
		self.resetResults()
		self.setResultsTitle("Missing Tags")
		rows = [ (r[0], r[2]) for r in self.tag_info if len(r[2]) > 0]
		self.grid = gridlib.Grid(self.panel)
		gridSizer = wx.BoxSizer(wx.HORIZONTAL)
		gridSizer.Add(self.grid, 1, wx.ALL|wx.EXPAND, 5)
		self.panel.GetSizer().Add(gridSizer, 0, wx.ALL|wx.EXPAND)
		self.grid.CreateGrid(len(rows), 2)
		self.grid.SetDefaultCellOverflow(False)
		self.grid.SetColLabelValue(0, "Filename")
		self.grid.SetColLabelValue(1, "Missing Tags")
		row_num = 0
		for row in rows:
			self.grid.SetCellValue(row_num, 0, row[0])
			self.grid.SetCellValue(row_num, 1, ", ".join(row[1]))
			attr = gridlib.GridCellAttr()
			attr.SetReadOnly(True)
			self.grid.SetRowAttr(row_num, attr)
			row_num += 1
		self.grid.AutoSize()
		self.panel.Layout()

	def setResultsTitle(self, text):
		if self.titleText is None:
			font = wx.Font(18, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.BOLD)
			self.titleText = wx.StaticText(self.panel, style=wx.ALIGN_CENTER)
			self.titleText.SetFont(font)
			titleSizer = wx.BoxSizer(wx.HORIZONTAL)
			titleSizer.Add(self.titleText, 1, wx.ALL|wx.EXPAND)
			self.panel.GetSizer().Add(titleSizer, 0, wx.ALL|wx.EXPAND)
		self.titleText.SetLabel(text)

	def setButtonStates(self):
		target_ok = os.path.isdir(self.target) or os.path.isfile(self.target)
		processing = self.workerThread is not None and not (self.workerThread.stopping or self.workerThread.done)
		self.startButton.Enable(target_ok and not processing)
		self.stopButton.Enable(processing)
		showButtonsState = (not processing) and len(self.tag_info) > 0
		for button in [self.showTagsButton, self.showBadTagsButton, self.showMissingTagsButton]:
			button.Enable(showButtonsState)

	def processCallback(self, callbackName, callbackData):
		if callbackName == "tags":
			self.fileCount += 1
			filename = callbackData["filename"]
			tags = callbackData["tags"]
			self.tag_info.append((filename, tags, callbackData["missingTags"], callbackData["badTags"]))
			self.StatusBar.SetStatusText("%s: %s: %s" % (self.fileCount, filename, ", ".join(tags)))
		elif callbackName == "done":
			self.errorCount = callbackData["errorCount"]
			status = "Done"
			if callbackData["wasStopped"]:
				status = "Stopped"
			self.StatusBar.SetStatusText("Files: %s; %s - total errors: %s" % (self.fileCount, status, self.errorCount))
			self.workerThread.done = True
			self.setButtonStates()
		else:
			logging.getLogger().error("Unknown callback name %s", callbackName)
			self.StatusBar.SetStatusText("Error: Unknown callback name %s" % (callbackName))
	
	def OnExit(self,e):
		self.Close(True)  # Close the frame.

class LogFrame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent, wx.ID_ANY, "Image Tags Log")
 
		# Add a panel so it looks the correct on all platforms
		panel = wx.Panel(self, wx.ID_ANY)
		log = wx.TextCtrl(panel, wx.ID_ANY, size=(300,100),
						  style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
 
		# Add widgets to a sizer        
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(log, 1, wx.ALL|wx.EXPAND, 5)
		panel.SetSizer(sizer)
 
		# redirect text here
		redir=RedirectText(log, threading.current_thread().ident)
		sys.stdout = redir
		sys.stderr = redir

		self.Bind(wx.EVT_CLOSE, self.OnClose)
 
	def OnClose(self,e):
		self.GetParent().logClosed()
		self.Destroy()
	
class TagsFrame(wx.Frame):
	def __init__(self, parent, config):
		wx.Frame.__init__(self, parent, wx.ID_ANY, "Tag Configuration")
		self.config = config
		self.dirty = False

		toolbar = self.CreateToolBar()

		self.applyButton = wx.Button(toolbar, label="Apply")
		toolbar.AddControl(self.applyButton)
		self.applyButton.Bind(wx.EVT_BUTTON, self.OnApply)

		self.saveButton = wx.Button(toolbar, label="Save")
		toolbar.AddControl(self.saveButton)
		self.saveButton.Bind(wx.EVT_BUTTON, self.OnSave)

		self.addButton = wx.Button(toolbar, label="Add")
		toolbar.AddControl(self.addButton)
		self.addButton.Bind(wx.EVT_BUTTON, self.OnAdd)

		toolbar.Realize()
		self.CreateStatusBar()

		# Add a panel so it looks the correct on all platforms
		self.panel = wx.Panel(self, wx.ID_ANY)
		panelSizer = wx.BoxSizer(wx.VERTICAL)
		self.panel.SetSizer(panelSizer)
		self.grid = gridlib.Grid(self.panel)
		gridSizer = wx.BoxSizer(wx.HORIZONTAL)
		gridSizer.Add(self.grid, 1, wx.ALL|wx.EXPAND, 5)
		self.panel.GetSizer().Add(gridSizer, 0, wx.ALL|wx.EXPAND)
		self.grid.SetDefaultCellOverflow(False)
		self.grid.SetColLabelValue(0, "Tag")
		self.grid.SetColLabelValue(1, "Is Required")
		self.grid.SetDefaultCellOverflow(False)
		all_tags = sorted(set(config.tags_allowed + config.tags_required))
		self.grid.CreateGrid(len(all_tags), 2)
		self.grid.SetColLabelValue(0, "Tag")
		self.grid.SetColLabelValue(1, "Required")
		attr = gridlib.GridCellAttr()
		attr.SetEditor(gridlib.GridCellBoolEditor())
		attr.SetRenderer(gridlib.GridCellBoolRenderer())
		self.grid.SetColAttr(1, attr)
		row_num = 0
		for tag in all_tags:
			self.grid.SetCellValue(row_num, 0, tag)
			cell_value = ""
			if tag in config.tags_required:
				cell_value = "1"
			self.grid.SetCellValue(row_num, 1, cell_value)
			row_num += 1
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnCellChanged)
		self.grid.AutoSize()
		self.panel.Layout()

	def OnApply(self, e):
		errors = self.apply2config()
		if errors == 0:
			self.StatusBar.SetStatusText("Tag info is applied (but not saved)")

	def apply2config(self):
		tags_allowed = []
		tags_required = []
		errors = 0
		for row_num in range(0, self.grid.GetNumberRows()):
			tag = self.grid.GetCellValue(row_num, 0)
			if len(tag) > 0:
				prop = self.grid.GetCellValue(row_num, 1)
				if tag in tags_allowed or tag in tags_required:
					self.StatusBar.SetStatusText("Error: Duplicate tag %s" % (tag))
					errors += 1
				else:
					if prop == '1':
						tags_required.append(tag)
					else:
						tags_allowed.append(tag)
		if errors == 0:
			self.config.tags_allowed = tags_allowed
			self.config.tags_required = tags_required
		return errors

	def OnSave(self, e):
		try:
			errors = self.apply2config()
			if errors == 0:
				self.StatusBar.SetStatusText("Tag info is applied and saved")
				self.config.save_config()
				self.dirty = False

		except Exception as exc:
			logging.getLogger().exception(exc)
	
	def OnAdd(self, e):
		self.grid.AppendRows()
		w, h = self.GetClientSize()
		self.SetSize((w, h))

	def OnCellChanged(self, e):
		self.dirty = True

	def OnClose(self, e):
		answer = wx.ID_YES
		if self.dirty:
			dlg = wx.MessageDialog(self, "The tags have been modified, but not saved. Close anyway?", 
				caption="Unsaved Tag Configuration Changes",
				style=wx.CANCEL|wx.YES_NO)
			answer = dlg.ShowModal()
		if answer == wx.ID_YES:
			self.GetParent().tagsClosed()
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
	def __init__(self, callback, args, target, config):
		super().__init__()
		self.callback = callback
		self.config = config
		self.errorCount = 0
		self.args = args
		self.target = target
		self.stopping = False
		self.done = False

	def run(self):
		self.photo_tags = phototags.PhotoTags(target_required=False, callback=self.callback, args=self.args, 
					tags_allowed=self.config.tags_allowed, tags_required=self.config.tags_required)
		if self.args.debug:
			self.photo_tags.logger.setLevel(logging.DEBUG)
		self.errorCount = self.photo_tags.process_target(self.target)
		self.done = True

	def stop(self):
		self.photo_tags.stop_processing()
		self.stopping = True

app = wx.App(False)
frame = MainWindow(None, "Image Tag Checker")
app.MainLoop()