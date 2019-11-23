#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.4 on Mon Oct  7 16:30:26 2019
#

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
import phototags
import logging, os, sys, threading, wx
import wx.grid as Grid
# end wxGlade

class TagsConfigFrame(wx.Frame):
	def __init__(self, *args, **kwds):
		# begin wxGlade: TagsConfigFrame.__init__
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
		wx.Frame.__init__(self, *args, **kwds)
		self.SetSize((400, 300))
		self.SetTitle("Tag Configuration")
		
		self.frame_tags_config_statusbar = self.CreateStatusBar(1)
		self.frame_tags_config_statusbar.SetStatusWidths([-1])
		
		sizer_1 = wx.BoxSizer(wx.VERTICAL)
		
		self.grid_config = wx.grid.Grid(self, wx.ID_ANY, size=(1, 1))
		self.grid_config.CreateGrid(0, 3)
		self.grid_config.SetColLabelValue(0, "Tag")
		self.grid_config.SetColLabelValue(1, "Required")
		self.grid_config.SetColLabelValue(2, "Kind")
		sizer_1.Add(self.grid_config, 1, wx.EXPAND, 0)
		
		sizer_18 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_1.Add(sizer_18, 0, wx.ALL, 15)
		
		self.button_add = wx.Button(self, wx.ID_ANY, "Add")
		self.button_add.SetToolTip("Add a row")
		sizer_18.Add(self.button_add, 0, 0, 0)
		
		self.button_apply = wx.Button(self, wx.ID_ANY, "Apply")
		self.button_apply.SetToolTip("Apply settings to current configuration")
		sizer_18.Add(self.button_apply, 0, 0, 0)
		
		self.button_save = wx.Button(self, wx.ID_ANY, "Save...")
		self.button_save.SetToolTip("Save to file")
		sizer_18.Add(self.button_save, 0, 0, 0)
		
		self.SetSizer(sizer_1)
		
		self.Layout()

		self.Bind(wx.grid.EVT_GRID_CMD_CELL_CHANGED, self.on_cell_changed, self.grid_config)
		self.Bind(wx.grid.EVT_GRID_CMD_CELL_CHANGING, self.on_cell_changing, self.grid_config)
		self.Bind(wx.EVT_BUTTON, self.on_add, self.button_add)
		self.Bind(wx.EVT_BUTTON, self.on_apply, self.button_apply)
		self.Bind(wx.EVT_BUTTON, self.on_save, self.button_save)
		# end wxGlade
		self.dirty = False
		self.config = None
		self.close_handler = None

	def set_config(self, config):
		self.config = config
		grid_table = TagConfigTable(config)
		self.grid_config.SetTable(grid_table, True)
		self.grid_config.SetDefaultCellOverflow(False)
		attr = Grid.GridCellAttr()
		attr.SetEditor(Grid.GridCellBoolEditor())
		attr.SetRenderer(Grid.GridCellBoolRenderer())
		self.grid_config.SetColAttr(1, attr)
		tag_kind_strings = ("literal", "wildcard", "regex")
		tag_kind_choices = ",".join(tag_kind_strings)
		attr = Grid.GridCellAttr()
		attr.SetEditor(Grid.GridCellEnumEditor(choices=tag_kind_choices))
		attr.SetRenderer(Grid.GridCellEnumRenderer(choices=tag_kind_choices))
		self.grid_config.SetColAttr(2, attr)

	def set_close_handler(self, close_handler):
		self.close_handler = close_handler
		self.Bind(wx.EVT_CLOSE, self.on_close)
	
	def on_close(self, event):
		answer = wx.ID_YES
		if self.dirty:
			dlg = wx.MessageDialog(self, "The tags have been modified, but not saved. Close anyway?", 
				caption="Unsaved Tag Configuration Changes",
				style=wx.CANCEL|wx.YES_NO)
			answer = dlg.ShowModal()
		if answer == wx.ID_YES:
			self.close_handler(event)

	def on_apply(self, event):  # wxGlade: TagsConfigFrame.<event_handler>
		errors = self.apply2config()
		if errors == 0:
			self.frame_tags_config_statusbar.SetStatusText("Tag info is applied (but not saved)")

	def on_save(self, event):  # wxGlade: TagsConfigFrame.<event_handler>
		try:
			errors = self.apply2config()
			if errors == 0:
				self.frame_tags_config_statusbar.SetStatusText("Tag info is applied and saved")
				self.config.save_config()
				self.dirty = False
		except Exception as exc:
			logging.getLogger().exception(exc)

	def on_add(self, event):  # wxGlade: TagsConfigFrame.<event_handler>
		self.grid_config.AppendRows()

	def on_cell_changed(self, event):  # wxGlade: TagsConfigFrame.<event_handler>
		self.dirty = True

	def apply2config(self):
		tags_allowed = []
		tags_required = []
		errors = 0
		for row_num in range(0, self.grid_config.GetNumberRows()):
			tag = self.grid_config.GetCellValue(row_num, 0)
			if len(tag) > 0:
				prop = self.grid_config.GetCellValue(row_num, 1)
				if tag in tags_allowed or tag in tags_required:
					self.frame_tags_config_statusbar.SetStatusText("Error: Duplicate tag %s" % (tag))
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

	def on_cell_changing(self, event):  # wxGlade: TagsConfigFrame.<event_handler>
		row = event.GetRow()
		col = event.GetCol()
		if col == 0:
			# Test for regular expression
			tagp_curr = self.grid_config.GetTable().get_tag_pattern(row)
			val = event.GetString()
			if len(val) > 0:
				tagp_new = phototags.TagPattern(val, tagp_curr.tag_kind, tagp_curr.is_required)
				if not tagp_new.is_pattern_valid():
						event.Veto()
		return False

# end of class TagsConfigFrame

class TagConfigTable(wx.grid.GridTableBase):

	def __init__(self, config):
		super().__init__()
		self.config = config
		self.tags = [tag for tag in config.tags]
		self.kind_map = {phototags.TagKind.LITERAL: 'literal', 
						phototags.TagKind.WILDCARD: 'wildcard', 
						phototags.TagKind.REGEX: 'regex'}
		self.col_names = ["Tag", "Required", "Kind"]
		self._rows = self.GetNumberRows()
		self._cols = self.GetNumberCols()

	def get_tag_pattern(self, idx):
		return self.tags[idx]

	def GetValue(self, row, col):
		"""
		GetValue(row, col) -> PyObject
		
		Must be overridden to implement accessing the table values as text.
		"""
		t = self.tags[row]
		if col == 0:
			return t.tag_pattern
		if col == 1:
			if t.is_required:
				return "1"
			return "0"
		if col == 2:
			return self.kind_map[t.tag_kind]
		raise ValueError

	def SetValue(self, row, col, value):
		"""
		SetValue(row, col, value)
		
		Must be overridden to implement setting the table values as text.
		"""
		t = self.tags[row]
		if col == 0:
			t.tag_pattern = value
		elif col == 1:
			if value == "1":
				t.is_required = True
			else:
				t.is_required = False
		elif col == 2:
			t.tag_kind = phototags.TagKind(int(value))

	def GetNumberRows(self):
		"""
		GetNumberRows() -> int
		
		Must be overridden to return the number of rows in the table.
		"""
		return len(self.tags)

	def GetNumberCols(self):
		"""
		GetNumberCols() -> int
		
		Must be overridden to return the number of columns in the table.
		"""
		return len(self.col_names)

	def GetColLabelValue(self, col):
		return self.col_names[col]

	def AppendRows(self, numRows=1):
		for i in range(0, numRows):
			tagp = phototags.TagPattern("", phototags.TagKind.LITERAL, False)
			self.tags.append(tagp)
			self.config.tags.add(tagp)
		self.ResetView(self.GetView())
		return True

	def ResetView(self, grid):
		"""
		(Grid) -> Reset the grid view.   Call this to
		update the grid if rows and columns have been added or deleted
		"""
		grid.BeginBatch()

		for current, new, delmsg, addmsg in [
			(self._rows, self.GetNumberRows(), Grid.GRIDTABLE_NOTIFY_ROWS_DELETED, Grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
			(self._cols, self.GetNumberCols(), Grid.GRIDTABLE_NOTIFY_COLS_DELETED, Grid.GRIDTABLE_NOTIFY_COLS_APPENDED),
		]:

			if new < current:
				msg = Grid.GridTableMessage(self,delmsg,new,current-new)
				grid.ProcessTableMessage(msg)
			elif new > current:
				msg = Grid.GridTableMessage(self,addmsg,new-current)
				grid.ProcessTableMessage(msg)
				self.UpdateValues(grid)

		grid.EndBatch()

		self._rows = self.GetNumberRows()
		self._cols = self.GetNumberCols()
		# update the column rendering plugins
		#self._updateColAttrs(grid)

		# update the scrollbars and the displayed part of the grid
		grid.AdjustScrollbars()
		grid.ForceRefresh()


	def UpdateValues(self, grid):
		"""Update all displayed values"""
		# This sends an event to the grid table to update all of the values
		msg = Grid.GridTableMessage(self, Grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
		grid.ProcessTableMessage(msg)

class MainWindow(wx.Frame):
	def __init__(self, *args, **kwds):
		# begin wxGlade: MainWindow.__init__
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
		wx.Frame.__init__(self, *args, **kwds)
		self.SetSize((694, 609))
		self.SetTitle("Phototags")
		_icon = wx.NullIcon
		_icon.CopyFromBitmap(wx.Bitmap(self.resource_path('./app-icon.jpg')))
		self.SetIcon(_icon)
		
		self.frame_statusbar = self.CreateStatusBar(1)
		self.frame_statusbar.SetStatusWidths([-1])
		# statusbar fields
		frame_statusbar_fields = ["frame_statusbar"]
		for i in range(len(frame_statusbar_fields)):
			self.frame_statusbar.SetStatusText(frame_statusbar_fields[i], i)
		
		sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		
		self.notebook_1 = wx.Notebook(self, wx.ID_ANY, style=wx.NB_BOTTOM)
		sizer_2.Add(self.notebook_1, 1, wx.ALL | wx.EXPAND, 5)
		
		self.options_page = wx.Panel(self.notebook_1, wx.ID_ANY)
		self.options_page.SetToolTip("Show/edit processing options")
		self.notebook_1.AddPage(self.options_page, "Options")
		
		sizer_3 = wx.BoxSizer(wx.VERTICAL)
		
		sizer_10 = wx.StaticBoxSizer(wx.StaticBox(self.options_page, wx.ID_ANY, "Options"), wx.VERTICAL)
		sizer_3.Add(sizer_10, 0, wx.ALL | wx.EXPAND, 15)
		
		sizer_11 = wx.BoxSizer(wx.VERTICAL)
		sizer_10.Add(sizer_11, 1, wx.EXPAND | wx.LEFT, 15)
		
		self.checkbox_file_tags = wx.CheckBox(self.options_page, wx.ID_ANY, "File tags")
		self.checkbox_file_tags.SetValue(1)
		self.checkbox_file_tags.arg_name = "print_file_tags"
		sizer_11.Add(self.checkbox_file_tags, 0, wx.TOP, 5)
		
		self.checkbox_check_allowed = wx.CheckBox(self.options_page, wx.ID_ANY, "Check allowed")
		self.checkbox_check_allowed.SetValue(1)
		self.checkbox_check_allowed.arg_name = "check_allowed"
		sizer_11.Add(self.checkbox_check_allowed, 0, wx.TOP, 5)
		
		self.checkbox_check_required = wx.CheckBox(self.options_page, wx.ID_ANY, "Check required")
		self.checkbox_check_required.SetValue(1)
		self.checkbox_check_required.arg_name = "check_required"
		sizer_11.Add(self.checkbox_check_required, 0, wx.TOP, 5)
		
		self.checkbox_check_frequency = wx.CheckBox(self.options_page, wx.ID_ANY, "Check frequency")
		self.checkbox_check_frequency.arg_name = "frequency"
		sizer_11.Add(self.checkbox_check_frequency, 0, wx.TOP, 5)
		
		sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_10.Add(sizer_5, 0, wx.LEFT, 15)
		
		self.text_ctrl_max_files = wx.TextCtrl(self.options_page, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB)
		self.text_ctrl_max_files.SetToolTip("Maximum number of files to process (or 'All')")
		self.text_ctrl_max_files.arg_name = "max_files"
		sizer_5.Add(self.text_ctrl_max_files, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP, 5)
		
		static_text_max_files = wx.StaticText(self.options_page, wx.ID_ANY, "Max files")
		sizer_5.Add(static_text_max_files, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.TOP, 5)
		
		sizer_6 = wx.StaticBoxSizer(wx.StaticBox(self.options_page, wx.ID_ANY, "Target"), wx.HORIZONTAL)
		sizer_10.Add(sizer_6, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 15)
		
		self.text_ctrl_target = wx.TextCtrl(self.options_page, wx.ID_ANY, "")
		self.text_ctrl_target.arg_name = "targ_arg"
		sizer_6.Add(self.text_ctrl_target, 1, wx.EXPAND, 0)
		
		self.button_select_target = wx.Button(self.options_page, wx.ID_ANY, "Select")
		sizer_6.Add(self.button_select_target, 0, wx.LEFT, 15)
		
		sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_10.Add(sizer_4, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.TOP, 15)
		
		self.apply_options_button = wx.Button(self.options_page, wx.ID_ANY, "Apply")
		self.apply_options_button.Enable(False)
		sizer_4.Add(self.apply_options_button, 0, wx.RIGHT, 10)
		
		self.revert_options_button = wx.Button(self.options_page, wx.ID_ANY, "Revert")
		self.revert_options_button.Enable(False)
		sizer_4.Add(self.revert_options_button, 0, wx.RIGHT, 10)
		
		sizer_18 = wx.StaticBoxSizer(wx.StaticBox(self.options_page, wx.ID_ANY, "Configuration"), wx.HORIZONTAL)
		sizer_3.Add(sizer_18, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
		
		sizer_19 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_18.Add(sizer_19, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
		
		self.button_edit_config = wx.Button(self.options_page, wx.ID_ANY, "Edit...")
		self.button_edit_config.SetToolTip("Edit tag configuration")
		sizer_19.Add(self.button_edit_config, 0, 0, 0)
		
		sizer_7 = wx.StaticBoxSizer(wx.StaticBox(self.options_page, wx.ID_ANY, "Processing"), wx.HORIZONTAL)
		sizer_3.Add(sizer_7, 0, wx.ALL, 15)
		
		self.button_start = wx.Button(self.options_page, wx.ID_ANY, "Start")
		sizer_7.Add(self.button_start, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
		
		self.button_stop = wx.Button(self.options_page, wx.ID_ANY, "Stop")
		self.button_stop.Enable(False)
		sizer_7.Add(self.button_stop, 0, wx.RIGHT | wx.TOP, 10)
		
		self.notebook_1_Tags = wx.Panel(self.notebook_1, wx.ID_ANY)
		self.notebook_1_Tags.SetToolTip("Show tags used by individual files")
		self.notebook_1.AddPage(self.notebook_1_Tags, "Tags")
		
		sizer_8 = wx.BoxSizer(wx.VERTICAL)
		
		self.static_text_tags_header = wx.StaticText(self.notebook_1_Tags, wx.ID_ANY, "Not yet set\n", style=wx.ALIGN_CENTER)
		self.static_text_tags_header.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		sizer_8.Add(self.static_text_tags_header, 0, wx.ALL, 15)
		
		sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_8.Add(sizer_9, 1, wx.EXPAND, 0)
		
		self.grid_tags = wx.grid.Grid(self.notebook_1_Tags, wx.ID_ANY, size=(1, 1))
		self.grid_tags.CreateGrid(0, 2)
		self.grid_tags.EnableEditing(0)
		self.grid_tags.EnableDragRowSize(0)
		self.grid_tags.SetSelectionMode(wx.grid.Grid.SelectRows)
		self.grid_tags.SetColLabelValue(0, "Filename")
		self.grid_tags.SetColLabelValue(1, "All Tags")
		sizer_9.Add(self.grid_tags, 1, wx.ALL | wx.EXPAND, 15)
		
		self.notebook_1_Missing = wx.Panel(self.notebook_1, wx.ID_ANY)
		self.notebook_1.AddPage(self.notebook_1_Missing, "Missing")
		
		sizer_12 = wx.BoxSizer(wx.VERTICAL)
		
		self.static_text_tags_missing_header = wx.StaticText(self.notebook_1_Missing, wx.ID_ANY, "Not yet set\n", style=wx.ALIGN_CENTER)
		self.static_text_tags_missing_header.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		sizer_12.Add(self.static_text_tags_missing_header, 0, wx.ALL, 15)
		
		sizer_13 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_12.Add(sizer_13, 1, wx.EXPAND, 0)
		
		self.grid_tags_missing = wx.grid.Grid(self.notebook_1_Missing, wx.ID_ANY, size=(1, 1))
		self.grid_tags_missing.CreateGrid(0, 2)
		self.grid_tags_missing.EnableEditing(0)
		self.grid_tags_missing.EnableDragRowSize(0)
		self.grid_tags_missing.SetSelectionMode(wx.grid.Grid.SelectRows)
		self.grid_tags_missing.SetColLabelValue(0, "Filename")
		self.grid_tags_missing.SetColLabelValue(1, "Missing Tags")
		sizer_13.Add(self.grid_tags_missing, 1, wx.ALL | wx.EXPAND, 15)
		
		self.notebook_1_Disallowed = wx.Panel(self.notebook_1, wx.ID_ANY, style=wx.BORDER_SIMPLE | wx.TAB_TRAVERSAL)
		self.notebook_1.AddPage(self.notebook_1_Disallowed, "Disallowed")
		
		sizer_14 = wx.BoxSizer(wx.VERTICAL)
		
		self.static_text_tags_bad_header = wx.StaticText(self.notebook_1_Disallowed, wx.ID_ANY, "Not yet set\n", style=wx.ALIGN_CENTER)
		self.static_text_tags_bad_header.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		sizer_14.Add(self.static_text_tags_bad_header, 0, wx.ALL, 15)
		
		sizer_16 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_14.Add(sizer_16, 1, wx.EXPAND, 0)
		
		self.grid_tags_bad = wx.grid.Grid(self.notebook_1_Disallowed, wx.ID_ANY, size=(1, 1))
		self.grid_tags_bad.CreateGrid(0, 2)
		self.grid_tags_bad.EnableEditing(0)
		self.grid_tags_bad.EnableDragRowSize(0)
		self.grid_tags_bad.SetSelectionMode(wx.grid.Grid.SelectRows)
		self.grid_tags_bad.SetColLabelValue(0, "Filename")
		self.grid_tags_bad.SetColLabelValue(1, "Missing Tags")
		sizer_16.Add(self.grid_tags_bad, 1, wx.ALL | wx.EXPAND, 15)
		
		self.notebook_1_Frequency = wx.Panel(self.notebook_1, wx.ID_ANY)
		self.notebook_1.AddPage(self.notebook_1_Frequency, "Frequency")
		
		sizer_15 = wx.BoxSizer(wx.VERTICAL)
		
		self.static_text_tags_freq_header = wx.StaticText(self.notebook_1_Frequency, wx.ID_ANY, "Not yet set\n", style=wx.ALIGN_CENTER)
		self.static_text_tags_freq_header.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		sizer_15.Add(self.static_text_tags_freq_header, 0, wx.ALL, 15)
		
		sizer_17 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_15.Add(sizer_17, 1, wx.EXPAND, 0)
		
		self.grid_tags_freq = wx.grid.Grid(self.notebook_1_Frequency, wx.ID_ANY, size=(1, 1))
		self.grid_tags_freq.CreateGrid(0, 2)
		self.grid_tags_freq.EnableEditing(0)
		self.grid_tags_freq.EnableDragRowSize(0)
		self.grid_tags_freq.SetSelectionMode(wx.grid.Grid.SelectRows)
		self.grid_tags_freq.SetColLabelValue(0, "Tag")
		self.grid_tags_freq.SetColLabelValue(1, "Frequency")
		#self.grid_tags_freq.UseNativeColHeader(True)
		sizer_17.Add(self.grid_tags_freq, 1, wx.ALL | wx.EXPAND, 15)
		
		self.notebook_1_logs = wx.ScrolledWindow(self.notebook_1, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.notebook_1_logs.SetScrollRate(10, 10)
		self.notebook_1.AddPage(self.notebook_1_logs, "Logs")
		
		sizer_1 = wx.BoxSizer(wx.VERTICAL)
		
		self.log_text_ctrl = wx.TextCtrl(self.notebook_1_logs, wx.ID_ANY, "", style=wx.TE_BESTWRAP | wx.TE_MULTILINE | wx.TE_READONLY)
		sizer_1.Add(self.log_text_ctrl, 1, wx.ALL | wx.EXPAND, 15)
		
		self.notebook_1_logs.SetSizer(sizer_1)
		
		self.notebook_1_Frequency.SetSizer(sizer_15)
		
		self.notebook_1_Disallowed.SetSizer(sizer_14)
		
		self.notebook_1_Missing.SetSizer(sizer_12)
		
		self.notebook_1_Tags.SetSizer(sizer_8)
		
		self.options_page.SetSizer(sizer_3)
		
		self.SetSizer(sizer_2)
		
		self.Layout()

		self.Bind(wx.EVT_CHECKBOX, self.on_options_event, self.checkbox_file_tags)
		self.Bind(wx.EVT_CHECKBOX, self.on_options_event, self.checkbox_check_allowed)
		self.Bind(wx.EVT_CHECKBOX, self.on_options_event, self.checkbox_check_required)
		self.Bind(wx.EVT_CHECKBOX, self.on_options_event, self.checkbox_check_frequency)
		self.Bind(wx.EVT_TEXT, self.on_options_event, self.text_ctrl_max_files)
		self.Bind(wx.EVT_TEXT, self.on_options_event, self.text_ctrl_target)
		self.Bind(wx.EVT_BUTTON, self.on_target_select, self.button_select_target)
		self.Bind(wx.EVT_BUTTON, self.on_apply_options, self.apply_options_button)
		self.Bind(wx.EVT_BUTTON, self.on_revert_options, self.revert_options_button)
		self.Bind(wx.EVT_BUTTON, self.on_edit_config, self.button_edit_config)
		self.Bind(wx.EVT_BUTTON, self.on_start_button, self.button_start)
		self.Bind(wx.EVT_BUTTON, self.on_stop_button, self.button_stop)
		# end wxGlade
		try:
			# redirect text here
			redir=RedirectText(self.log_text_ctrl, threading.current_thread().ident)
			sys.stdout = redir
			sys.stderr = redir
			self.worker_thread = None
			self.tag_config_frame = None
			self.guiThreadId = threading.current_thread().ident
			self.args = self.parseArgs()
			self.update_options()
			self.config = phototags.PhotoTagsConfig()
			self.config.read_config(self.args.config)
			self.reset_results()
			self.set_button_states()
			self.GetStatusBar().SetStatusText("")
			self.SetMinClientSize((600, 480))
			self.SetClientSize((600, 480))
		except Exception as exc:
			self.GetStatusBar().SetStatusText("Error: "+str(exc))
		print("App starting")


	def __set_properties(self):
		pass

	def __do_layout(self):
		pass

	def parseArgs(self):
		parser = phototags.initArgParser()
		parser.add_argument('--target', default=".", dest='targ_arg', help="File or directory to check")
		return parser.parse_args()

	def options_ok(self):
		return self.max_files_ok() and self.target_ok()

	def max_files_ok(self):
		val_str = self.text_ctrl_max_files.GetValue().strip()
		if len(val_str) > 0 and val_str.lower() != "all":
			try:
				val = int(val_str)
			except Exception as exc:
				return False
		return True

	def target_ok(self):
		target = self.text_ctrl_target.GetValue().strip()
		return os.path.isdir(target) or os.path.isfile(target)

	def on_apply_options(self, event):  # wxGlade: MainWindow.<event_handler>
		page = self.options_page.GetChildren()
		option_controls = [c for c in self.options_page.GetChildren() if hasattr(c, "arg_name")]
		# Check validity of some fields
		errors = 0
		for i in option_controls:
			arg_name = getattr(i, "arg_name")
			if arg_name == "max_files":
				if not self.max_files_ok():
					val_str = i.GetValue()
					msg = wx.MessageDialog(self, "Illegal value \"%s\". Use \"All\" or a positive number." % (val_str), "Max Files Error")
					msg.ShowModal()
					errors += 1
			elif arg_name == "targ_arg":
				val_str = i.GetValue().strip()
				if not self.target_ok():
					msg = wx.MessageDialog(self, "\"%s\" is not a file or directory." % (val_str), "Target Error")
					msg.ShowModal()
					errors += 1
		# If no errors then apply the control values to the args object
		if errors == 0:
			for i in option_controls:
				if hasattr(i, "arg_name"):
					arg_name = getattr(i, "arg_name")
					if arg_name == "max_files":
						val = -1
						val_str = i.GetValue().strip()
						if len(val_str) > 0 and val_str.lower() != "all":
							val = int(val_str)
						setattr(self.args, arg_name, val)
					elif arg_name == "targ_arg":
						self.args.targ_arg = i.GetValue().strip()
					else:
						setattr(self.args, arg_name, bool(i.GetValue()))
			self.options_modified = False
			self.set_button_states()
			self.GetStatusBar().SetStatusText("Option settings applied")
		else:
			self.GetStatusBar().SetStatusText("Could not apply option settings")

	def on_revert_options(self, event):  # wxGlade: MainWindow.<event_handler>
		self.update_options()
		self.options_modified = False
		self.set_button_states()
		self.GetStatusBar().SetStatusText("Options reverted to previous settings")
	
	def on_options_event(self, event):  # wxGlade: MainWindow.<event_handler>
		self.options_modified = True
		self.set_button_states()

	def update_options(self):
		# Update control values from saved args
		page = self.options_page.GetChildren()
		for i in page:
			if hasattr(i, "arg_name"):
				arg_name = getattr(i, "arg_name")
				arg_value = getattr(self.args, arg_name)
				if arg_name == "max_files":
					str_value = str(arg_value)
					if arg_value < 0:
						str_value = "All"
					i.ChangeValue(str_value) # avoids triggering event
				elif hasattr(i, "ChangeValue"):
					i.ChangeValue(arg_value) # avoids triggering event
				else:
					i.SetValue(arg_value)
		self.options_modified = False

	def on_start_button(self, event):  # wxGlade: MainWindow.<event_handler>
		self.GetStatusBar().SetStatusText("Starting to process images...")
		self.reset_results()
		self.worker_thread = PhotoTagsThread(self.processCallback, self.args, self.args.targ_arg, self.config)
		self.worker_thread.start()
		self.set_button_states()

	def reset_results(self):
		self.tag_info = []
		self.fileCount = 0
		self.static_text_tags_header.SetLabelText("No results yet")
		self.static_text_tags_missing_header.SetLabelText("No results yet")
		self.static_text_tags_bad_header.SetLabelText("No results yet")
		self.grid_tags.Hide()
		self.grid_tags_missing.Hide()
		self.grid_tags_bad.Hide()
		self.grid_tags_freq.Hide()

	def set_button_states(self):
		options_ok = self.options_ok()
		apply_revert = self.options_modified
		start = options_ok and not self.options_modified and \
				(self.worker_thread is None or \
				self.worker_thread.done)
		stop = self.worker_thread is not None and \
				not self.worker_thread.done

		self.apply_options_button.Enable(apply_revert)
		self.revert_options_button.Enable(apply_revert)
		self.button_start.Enable(start)
		self.button_stop.Enable(stop)

	def update_results(self):
		self.update_tag_page()
		self.update_tags_missing_page()
		self.update_tags_disallowed_page()
		self.update_tags_freq_page()

	def update_tag_page(self):
		if self.options_modified:
			self.static_text_tags_header.SetLabelText("Options were modified; results are not valid.")
			self.grid_tags.Hide()
		elif not self.args.print_file_tags:
			self.static_text_tags_header.SetLabelText("Options did not include \"file tags\"")
			self.grid_tags.Hide()
		else:
			excess = len(self.tag_info) - self.grid_tags.GetNumberRows()
			if excess > 0:
				self.grid_tags.AppendRows(excess)
			row_num = 0
			for row in self.tag_info:
				self.grid_tags.SetCellValue(row_num, 0, row[0])
				self.grid_tags.SetCellValue(row_num, 1, ", ".join(row[1]))
				attr = Grid.GridCellAttr()
				attr.SetReadOnly(True)
				self.grid_tags.SetRowAttr(row_num, attr)
				row_num += 1
			self.static_text_tags_header.SetLabelText("Tags Per File")
			self.grid_tags.AutoSize()
			self.grid_tags.Show()

	def update_tags_missing_page(self):
		if self.options_modified:
			self.static_text_tags_missing_header.SetLabelText("Options were modified; results are not valid.")
			self.grid_tags_missing.Hide()
		elif not self.args.check_required:
			self.static_text_tags_missing_header.SetLabelText("Options did not include \"check required tags\"")
			self.grid_tags_missing.Hide()
		else:
			rows = [ (r[0], r[2]) for r in self.tag_info if len(r[2]) > 0]
			excess = len(rows) - self.grid_tags_missing.GetNumberRows()
			if excess > 0:
				self.grid_tags_missing.AppendRows(excess)
			row_num = 0
			for row in rows:
				self.grid_tags_missing.SetCellValue(row_num, 0, row[0])
				self.grid_tags_missing.SetCellValue(row_num, 1, ", ".join([p.ini_pattern() for p in row[1]]))
				attr = Grid.GridCellAttr()
				attr.SetReadOnly(True)
				self.grid_tags_missing.SetRowAttr(row_num, attr)
				row_num += 1
			self.static_text_tags_missing_header.SetLabelText("Missing Tags")
			self.grid_tags_missing.AutoSize()
			self.grid_tags_missing.Show()

	def update_tags_disallowed_page(self):
		if self.options_modified:
			self.static_text_tags_bad_header.SetLabelText("Options were modified; results are not valid.")
			self.grid_tags_bad.Hide()
		elif not self.args.check_allowed:
			self.static_text_tags_bad_header.SetLabelText("Options did not include \"check allowed tags\"")
			self.grid_tags_bad.Hide()
		else:
			rows = [ (r[0], r[3]) for r in self.tag_info if len(r[3]) > 0]
			excess = len(rows) - self.grid_tags_bad.GetNumberRows()
			if excess > 0:
				self.grid_tags_bad.AppendRows(excess)
			row_num = 0
			for row in rows:
				self.grid_tags_bad.SetCellValue(row_num, 0, row[0])
				self.grid_tags_bad.SetCellValue(row_num, 1, ", ".join(row[1]))
				attr = Grid.GridCellAttr()
				attr.SetReadOnly(True)
				self.grid_tags_bad.SetRowAttr(row_num, attr)
				row_num += 1
			self.static_text_tags_bad_header.SetLabelText("Disallowed Tags")
			self.grid_tags_bad.AutoSize()
			self.grid_tags_bad.Show()

	def update_tags_freq_page(self):
		if self.options_modified:
			self.static_text_tags_freq_header.SetLabelText("Options were modified; results are not valid.")
			self.grid_tags_freq.Hide()
		elif not self.args.frequency:
			self.static_text_tags_freq_header.SetLabelText("Options did not include \"check frequency\"")
			self.grid_tags_freq.Hide()
		else:
			rows = [ item for item in self.worker_thread.photo_tags.tag_stats.freq_dict.items()]
			excess = len(rows) - self.grid_tags_freq.GetNumberRows()
			if excess > 0:
				self.grid_tags_freq.AppendRows(excess)
			row_num = 0
			for row in rows:
				self.grid_tags_freq.SetCellValue(row_num, 0, row[0])
				self.grid_tags_freq.SetCellValue(row_num, 1, str(row[1]))
				attr = Grid.GridCellAttr()
				attr.SetReadOnly(True)
				self.grid_tags_freq.SetRowAttr(row_num, attr)
				row_num += 1
			self.static_text_tags_freq_header.SetLabelText("Tag Frequency")
			self.grid_tags_freq.AutoSize()
			self.grid_tags_freq.Show()

	def processCallback(self, callbackName, callbackData):
		if callbackName == "tags":
			self.fileCount += 1
			filename = callbackData["filename"]
			tags = callbackData["tags"]
			self.tag_info.append((filename, tags, callbackData["missingTags"], callbackData["badTags"]))
			self.GetStatusBar().SetStatusText("%s: %s: %s" % (self.fileCount, filename, ", ".join(tags)))
		elif callbackName == "done":
			self.errorCount = callbackData["errorCount"]
			status = "Done"
			if callbackData["wasStopped"]:
				status = "Stopped"
			self.GetStatusBar().SetStatusText("Processed %s files; %s - total errors: %s" % (self.fileCount, status, self.errorCount))
			self.worker_thread.done = True
			self.update_results()
			self.set_button_states()
		else:
			logging.getLogger().error("Unknown callback name %s", callbackName)
			self.GetStatusBar().SetStatusText("Error: Unknown callback name %s" % (callbackName))

	def on_stop_button(self, event):  # wxGlade: MainWindow.<event_handler>
		self.worker_thread.stop()
		self.GetStatusBar().SetStatusText("Stopping...")
		self.set_button_states()

	def on_target_select(self, event):  # wxGlade: MainWindow.<event_handler>
		dlg = wx.DirDialog(self, "Select a target directory for searching photos", "", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST )
		dlg.ShowModal()
		target = dlg.GetPath()
		self.text_ctrl_target.SetValue(target)

	def on_edit_config(self, event):  # wxGlade: MainWindow.<event_handler>
		self.tag_config_frame = TagsConfigFrame(self)
		self.tag_config_frame.set_config(self.config)
		self.tag_config_frame.set_close_handler(self.on_edit_config_close)
		self.tag_config_frame.Show()
		self.button_edit_config.Disable()

	def on_edit_config_close(self, event):
		self.tag_config_frame.Destroy()
		self.tag_config_frame = None
		self.button_edit_config.Enable()

	def resource_path(self, relative_path):
			""" Get absolute path to resource, works for dev and for PyInstaller """
			try:
					# PyInstaller creates a temp folder and stores path in _MEIPASS
					base_path = sys._MEIPASS
			except Exception:
					base_path = os.path.abspath(".")

			return os.path.join(base_path, relative_path)
# end of class MainWindow

class Phototags(wx.App):
	def OnInit(self):
		self.frame = MainWindow(None, wx.ID_ANY, "")
		self.SetTopWindow(self.frame)
		self.frame.Show()
		return True


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
					tag_patterns=self.config.tag_patterns)
		if self.args.debug:
			self.photo_tags.logger.setLevel(logging.DEBUG)
		self.errorCount = self.photo_tags.process_target(self.target)
		self.done = True

	def stop(self):
		self.photo_tags.stop_processing()
		self.stopping = True

# end of class Phototags

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

if __name__ == "__main__":
	myApp = Phototags(0)
	myApp.MainLoop()
