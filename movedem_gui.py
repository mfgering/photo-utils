#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.9pre on Wed Nov 27 11:39:19 2019
#

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
import movedem
import abc, logging, os, sys, threading, wx, wx.lib.mixins.listctrl
import wx.grid as Grid
# end wxGlade

class MainWindow(wx.Frame):
	def __init__(self, *args, **kwds):
		# begin wxGlade: MainWindow.__init__
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
		wx.Frame.__init__(self, *args, **kwds)
		self.SetSize((928, 654))
		self.SetTitle("Moved Some Files -- Let's Check 'Em")
		
		self.frame_statusbar = self.CreateStatusBar(1)
		self.frame_statusbar.SetStatusWidths([-1])
		
		main_sizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.notebook_1 = wx.Notebook(self, wx.ID_ANY)
		main_sizer.Add(self.notebook_1, 1, wx.EXPAND, 0)
		
		self.options_page = wx.Panel(self.notebook_1, wx.ID_ANY)
		self.options_page.SetToolTip("Show/edit processing options")
		self.notebook_1.AddPage(self.options_page, "Options")
		
		sizer_3 = wx.BoxSizer(wx.VERTICAL)
		
		sizer_10 = wx.StaticBoxSizer(wx.StaticBox(self.options_page, wx.ID_ANY, "Options"), wx.VERTICAL)
		sizer_3.Add(sizer_10, 0, wx.ALL | wx.EXPAND, 15)
		
		sizer_11 = wx.BoxSizer(wx.VERTICAL)
		sizer_10.Add(sizer_11, 1, wx.EXPAND | wx.LEFT, 15)
		
		self.checkbox_compare = wx.CheckBox(self.options_page, wx.ID_ANY, "Compare old and new directories")
		self.checkbox_compare.SetValue(1)
		self.checkbox_compare.arg_name = "compare"
		sizer_11.Add(self.checkbox_compare, 0, wx.TOP, 5)
		
		sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_10.Add(sizer_5, 0, wx.LEFT, 15)
		
		self.text_ctrl_max_files = wx.TextCtrl(self.options_page, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB)
		self.text_ctrl_max_files.SetToolTip("Maximum number of files to process (or 'All')")
		self.text_ctrl_max_files.arg_name = "max_files"
		sizer_5.Add(self.text_ctrl_max_files, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP, 5)
		
		static_text_max_files = wx.StaticText(self.options_page, wx.ID_ANY, "Max files")
		sizer_5.Add(static_text_max_files, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.TOP, 5)
		
		sizer_6 = wx.StaticBoxSizer(wx.StaticBox(self.options_page, wx.ID_ANY, "Directories"), wx.VERTICAL)
		sizer_10.Add(sizer_6, 0, wx.ALL | wx.EXPAND, 15)
		
		sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_6.Add(sizer_1, 0, wx.ALL | wx.EXPAND, 5)
		
		static_text_1 = wx.StaticText(self.options_page, wx.ID_ANY, "Old:", style=wx.ALIGN_LEFT)
		sizer_1.Add(static_text_1, 0, wx.RIGHT, 10)
		
		self.text_ctrl_old_dir = wx.TextCtrl(self.options_page, wx.ID_ANY, "")
		self.text_ctrl_old_dir.arg_name = "dir_old"
		sizer_1.Add(self.text_ctrl_old_dir, 1, wx.EXPAND, 0)
		
		self.button_select_old_dir = wx.Button(self.options_page, wx.ID_ANY, "Select...")
		sizer_1.Add(self.button_select_old_dir, 0, wx.LEFT, 15)
		
		sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_6.Add(sizer_2, 1, wx.ALL | wx.EXPAND, 5)
		
		static_text_2 = wx.StaticText(self.options_page, wx.ID_ANY, "New:", style=wx.ALIGN_LEFT)
		sizer_2.Add(static_text_2, 0, wx.RIGHT, 10)
		
		self.text_ctrl_new_dir = wx.TextCtrl(self.options_page, wx.ID_ANY, "")
		self.text_ctrl_new_dir.arg_name = "dir_new"
		sizer_2.Add(self.text_ctrl_new_dir, 1, wx.EXPAND, 0)
		
		self.button_select_new_dir = wx.Button(self.options_page, wx.ID_ANY, "Select...")
		sizer_2.Add(self.button_select_new_dir, 0, wx.LEFT, 15)
		
		sizer_7 = wx.StaticBoxSizer(wx.StaticBox(self.options_page, wx.ID_ANY, "Processing"), wx.HORIZONTAL)
		sizer_3.Add(sizer_7, 0, wx.ALL, 15)
		
		self.button_start = wx.Button(self.options_page, wx.ID_ANY, "Start")
		sizer_7.Add(self.button_start, 0, wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.LEFT, 10)
		
		self.button_stop = wx.Button(self.options_page, wx.ID_ANY, "Stop")
		self.button_stop.Enable(False)
		sizer_7.Add(self.button_stop, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT, 10)
		
		self.unmatched_page = wx.Panel(self.notebook_1, wx.ID_ANY)
		self.unmatched_page.SetToolTip("Old files without matching new files\n")
		self.notebook_1.AddPage(self.unmatched_page, "Unmatched")
		
		sizer_8 = wx.BoxSizer(wx.VERTICAL)
		
		self.static_text_unmatched_header = wx.StaticText(self.unmatched_page, wx.ID_ANY, "Not yet set\n", style=wx.ALIGN_CENTER)
		self.static_text_unmatched_header.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		sizer_8.Add(self.static_text_unmatched_header, 0, wx.ALL, 15)
		
		sizer_13 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_8.Add(sizer_13, 1, wx.EXPAND, 0)
		
		self.list_ctrl_unmatched = UnmatchedFilesListCtrl(self.unmatched_page, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_VRULES)
		sizer_13.Add(self.list_ctrl_unmatched, 1, wx.EXPAND, 0)
		
		self.matches_page = wx.Panel(self.notebook_1, wx.ID_ANY)
		self.matches_page.SetToolTip("Files that match in old and new directories")
		self.notebook_1.AddPage(self.matches_page, "Matched")
		
		sizer_4 = wx.BoxSizer(wx.VERTICAL)
		
		self.static_text_matches_header = wx.StaticText(self.matches_page, wx.ID_ANY, "Not yet set\n", style=wx.ALIGN_CENTER)
		self.static_text_matches_header.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		sizer_4.Add(self.static_text_matches_header, 0, wx.ALL, 15)
		
		sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_4.Add(sizer_12, 1, wx.EXPAND, 0)
		
		self.list_ctrl_matches = MatchedFilesListCtrl(self.matches_page, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_VRULES)
		self.list_ctrl_matches.SetToolTip("Sort by clicking column headers, drag/drop columns to re-order.")
		sizer_12.Add(self.list_ctrl_matches, 1, wx.EXPAND, 0)
		
		self.updated_page = wx.Panel(self.notebook_1, wx.ID_ANY)
		self.updated_page.SetToolTip("Files with the same name, different contents")
		self.notebook_1.AddPage(self.updated_page, "Updated")
		
		sizer_14 = wx.BoxSizer(wx.VERTICAL)
		
		self.static_text_updated_header = wx.StaticText(self.updated_page, wx.ID_ANY, "Not yet set\n", style=wx.ALIGN_CENTER)
		self.static_text_updated_header.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		self.static_text_updated_header.SetToolTip("Files that have the same name, but different contents")
		sizer_14.Add(self.static_text_updated_header, 0, wx.ALL, 15)
		
		sizer_15 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_14.Add(sizer_15, 1, wx.EXPAND, 0)
		
		self.list_ctrl_updated = UpdatedFilesListCtrl(self.updated_page, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_VRULES)
		self.list_ctrl_updated.SetToolTip("Sort by clicking column headers.")
		sizer_15.Add(self.list_ctrl_updated, 1, wx.EXPAND, 0)
		
		self.notebook_1_logs = wx.ScrolledWindow(self.notebook_1, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.notebook_1_logs.SetScrollRate(10, 10)
		self.notebook_1.AddPage(self.notebook_1_logs, "Log")
		
		sizer_9 = wx.BoxSizer(wx.VERTICAL)
		
		self.log_text_ctrl = wx.TextCtrl(self.notebook_1_logs, wx.ID_ANY, "", style=wx.TE_BESTWRAP | wx.TE_MULTILINE | wx.TE_READONLY)
		sizer_9.Add(self.log_text_ctrl, 1, wx.ALL | wx.EXPAND, 15)
		
		self.notebook_1_logs.SetSizer(sizer_9)
		
		self.updated_page.SetSizer(sizer_14)
		
		self.matches_page.SetSizer(sizer_4)
		
		self.unmatched_page.SetSizer(sizer_8)
		
		self.options_page.SetSizer(sizer_3)
		
		self.SetSizer(main_sizer)
		
		self.Layout()

		self.Bind(wx.EVT_CHECKBOX, self.on_options_event, self.checkbox_compare)
		self.Bind(wx.EVT_TEXT, self.on_options_event, self.text_ctrl_max_files)
		self.Bind(wx.EVT_TEXT, self.on_options_event, self.text_ctrl_old_dir)
		self.Bind(wx.EVT_BUTTON, self.on_dir_select, self.button_select_old_dir)
		self.Bind(wx.EVT_TEXT, self.on_options_event, self.text_ctrl_new_dir)
		self.Bind(wx.EVT_BUTTON, self.on_dir_select, self.button_select_new_dir)
		self.Bind(wx.EVT_BUTTON, self.on_start_button, self.button_start)
		self.Bind(wx.EVT_BUTTON, self.on_stop_button, self.button_stop)
		self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_rclick_item, self.list_ctrl_matches)
		self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_rclick_item, self.list_ctrl_updated)
		# end wxGlade
		self.status_timer = None
		try:
			# redirect text here
			redir=RedirectText(self.log_text_ctrl, threading.current_thread().ident)
			sys.stdout = redir
			sys.stderr = redir
			self.worker_thread = None
			self.guiThreadId = threading.current_thread().ident
			self.args = self.parseArgs()
			self.update_options()
			self.reset_results()
			self.set_button_states()
			self.SetMinClientSize((600, 480))
			self.SetClientSize((600, 480))
		except Exception as exc:
			self.set_status("Error: "+str(exc))
			logging.getLogger().exception(exc)
		print("App starting")

	def set_button_states(self):
		#self.set_status("") #TODO: DELETE
		options_ok = self.options_ok()
		start = options_ok and \
				(self.worker_thread is None or \
				self.worker_thread.done)
		stop = self.worker_thread is not None and \
				not self.worker_thread.done
		self.button_start.Enable(start)
		self.button_stop.Enable(stop)

	def parseArgs(self):
		parser = movedem.initArgParser()
		return parser.parse_args()

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

	def options_ok(self):
		return self.max_files_ok() and self.dirs_ok()

	def max_files_ok(self):
		val_str = self.text_ctrl_max_files.GetValue().strip()
		if len(val_str) > 0 and val_str.lower() != "all":
			try:
				val = int(val_str)
				self.args.max_files = val
			except Exception as exc:
				self.set_status("max files must be a positive integer or \"all\"", 3000)
				return False
		return True

	def dirs_ok(self):
		for dir_ctl in (self.text_ctrl_old_dir, self.text_ctrl_new_dir):
			dir = dir_ctl.GetValue().strip()
			if not os.path.isdir(dir):
				self.set_status(f"'{dir}' is not a valid directory.", 3000)
				return False
		return True

	def reset_results(self):
		self.file_count = 0
		self.static_text_matches_header.SetLabelText("No results yet")
		#self.static_text_tags_header.SetLabelText("No results yet")
		#self.static_text_tags_missing_header.SetLabelText("No results yet")
		#self.static_text_tags_bad_header.SetLabelText("No results yet")
		#self.grid_tags.Hide()
		#self.grid_tags_missing.Hide()
		#self.grid_tags_bad.Hide()
		#self.grid_tags_freq.Hide()

	def on_options_event(self, event):  # wxGlade: MainWindow.<event_handler>
		self.set_button_states()

	def on_dir_select(self, event):  # wxGlade: MainWindow.<event_handler>
		msg = "Select a directory for \"new\" content."
		text_ctrl = self.text_ctrl_new_dir
		if event.GetEventObject() == self.button_select_old_dir:
			msg = "Select a directory for \"old\" content."
			text_ctrl = self.text_ctrl_old_dir
		dlg = wx.DirDialog(self, msg, "", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST )
		if dlg.ShowModal() == wx.ID_OK:
			dir = dlg.GetPath()
			text_ctrl.SetValue(dir)
			self.set_status("") #TODO: REMOVE?
			self.set_button_states()
		dlg.Destroy()

	def process_callback(self, callback_name, callback_data):
		if callback_name == "file":
			self.file_count = self.file_count + 1
		elif callback_name == "start_compare":
			self.dir_data_old = callback_data["dir_data_old"]
			self.dir_data_new = callback_data["dir_data_new"]
			old_len = len(self.dir_data_old.file_data)
			new_len = len(self.dir_data_new.file_data)
			self.set_status("Starting to compare %s files (%s old and %s new)" 
						% (str(old_len+new_len), str(old_len), str(new_len)))
		elif callback_name == "file_check":
			cnt = callback_data["file_count"]
			total = callback_data["total_files"]
	
			self.set_status("Checked {} of {} ({:.0%} files)".format(cnt, total, cnt/total), 5000)
		elif callback_name == "compare_results":
			self.compare_results = callback_data
		elif callback_name == "done":
			status = "Done"
			if callback_data["wasStopped"]:
				status = "Stopped"
			self.set_status(f"Processed {self.file_count} files: {status}")
			self.worker_thread.done = True
			wx.CallAfter(self.update_results)
			self.set_button_states()
		else:
			logging.getLogger().error("Unknown callback name %s" % callback_name)
			self.set_status("Error: Unknown callback name %s" % (callback_name))

	def on_start_button(self, event):  # wxGlade: MainWindow.<event_handler>
		self.set_status("Starting to process directories...", 4000)
		self.reset_results()
		self.gui2args()
		self.worker_thread = MovedEmThread(self.process_callback, args=self.args)
		self.worker_thread.start()
		self.set_button_states()
		
	def on_stop_button(self, event):  # wxGlade: MainWindow.<event_handler>
		self.worker_thread.stop()
		self.set_status("Stopping...", 4000)
		self.set_button_states()

	def gui2args(self):
		option_controls = [c for c in self.options_page.GetChildren() if hasattr(c, "arg_name")]
		for i in option_controls:
			if hasattr(i, "arg_name"):
				arg_name = getattr(i, "arg_name")
				if arg_name == "max_files":
					val = -1
					val_str = i.GetValue().strip()
					if len(val_str) > 0 and val_str.lower() != "all":
						val = int(val_str)
					setattr(self.args, arg_name, val)
				elif arg_name == "dir_old" or arg_name == "dir_new":
					setattr(self.args, arg_name, i.GetValue())
				else:
					setattr(self.args, arg_name, bool(i.GetValue()))

	def update_results(self):
		if self.args.compare:
			self.update_matches_page()
			self.update_not_matched_page()
			self.update_updated_page()

	def update_matches_page(self):
		self.static_text_matches_header.SetLabelText("Matching Files")
		self.list_ctrl_matches.set_items(self.compare_results["same"])

	def update_not_matched_page(self):
		self.static_text_unmatched_header.SetLabelText("Unmatched Files")
		self.list_ctrl_unmatched.set_items(self.compare_results["not_matched"])

	def update_updated_page(self):
		self.static_text_updated_header.SetLabelText("Possibly Updated Files")
		self.list_ctrl_updated.set_items(self.compare_results["not_matched"])

	def set_status(self, msg, timeout=-1, timeout_msg=None):
		if self.status_timer is not None:
			del self.status_timer
			self.status_timer = None
		self.GetStatusBar().SetStatusText(msg)
		if timeout > 0:
			self.status_timeout_msg = timeout_msg
			threadId = threading.current_thread().ident
			if self.guiThreadId == threadId:
				self.status_timer = wx.CallLater(timeout, self.status_timed_out, msg=timeout_msg)
			else:
				wx.CallAfter(wx.CallLater, timeout, self.status_timed_out, msg=timeout_msg)			

	def status_timed_out(self, msg=None):
		if self.status_timer is not None:
			if msg is None:
				msg = ""
			self.GetStatusBar().SetStatusText(msg)
			del self.status_timer
			self.status_timer = None
		
	def on_rclick_item(self, event):  # wxGlade: MainWindow.<event_handler>
		print("Event handler 'on_rclick_item' not implemented!")
		event.Skip()
# end of class MainWindow

class AbstractFileInfoListCtrl(wx.ListView, wx.lib.mixins.listctrl.ColumnSorterMixin, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
	# http://code.activestate.com/recipes/426407-columnsortermixin-with-a-virtual-wxlistctrl/
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.LC_ICON, validator=wx.DefaultValidator, name=wx.ListCtrlNameStr):
		wx.ListCtrl.__init__(self, parent, id, pos, size, style, validator, name)
		wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)
		col_names = self.get_column_names()
		col_widths = self.get_column_widths()
		for i in range(len(col_names)):
			self.InsertColumn(i, col_names[i])
			self.SetColumnWidth(i, col_widths[i])
		self.col_sort_mixin = wx.lib.mixins.listctrl.ColumnSorterMixin.__init__(self, len(col_names))
		self.itemIndexMap = {}

	@abc.abstractmethod
	def get_column_names(self):
		"""Return a list of column name strings"""

	@abc.abstractmethod
	def get_column_widths(self):
		"""Return a list of column width integers"""

	def GetListCtrl(self):
		return self
	
	def GetColumnCount(self):
		return len(self.get_column_names())

	def OnGetItemAttr(self, item):
		return None

	def OnGetItemImage(self, item):
		return -1

	def OnGetItemText(self, item, col):
		return self.get_text_val(item, col)

	@abc.abstractmethod
	def get_text_val(self, item_idx, col, mapped=True):
		"""Must be overridden"""

	def GetColumnSorter(self):
		return self._my_col_sorter
	
	def _my_col_sorter(self, key):
		return self.get_text_val(key, self._col, mapped=False)

	def SortItems(self, sorter):
		self.sort_col, self.sort_flag = self.GetSortState()
		new_map = sorted(self.itemIndexMap, key=self._my_col_sorter, reverse=self.sort_flag)
		self.itemIndexMap = new_map
		self.Refresh()

	def _check_order(self, map, is_reversed, col):
		"""This is for debugging"""
		val = None
		for i in range(len(map)):
			idx_mapped = map[i]
			item = self.items[idx_mapped]
			prev_val = val
			val = self.get_text_val(idx_mapped, col, mapped=False)
			print("%s[%s]: %s" % (str(i), str(idx_mapped), val))
			if prev_val is not None:
				if is_reversed:
					is_ok = prev_val >= val
				else:
					is_ok = prev_val <= val
				if not is_ok:
					print("%s: prev: %s, curr: %s" % (str(i), prev_val, val))

	def set_items(self, items):
		self.items = items
		self.SetItemCount(len(items))
		self.itemIndexMap = [x for x in range(len(items))]

class UnmatchedFilesListCtrl(AbstractFileInfoListCtrl):
	def get_column_names(self):
		return ("Old", "New Name Matches")

	def get_column_widths(self):
		return (400, 100)

	def get_text_val(self, item_idx, col, mapped=True):
		if mapped:
			index = self.itemIndexMap[item_idx]
		else:
			index = item_idx
		data = self.items[index]
		if col == 0:
			val = data.get_full_fn()
		elif col == 1:
			maybe = data.get_maybe_updated()
			if maybe is None:
				val = str(0)
			else:
				val = str(len(maybe))
		else:
			raise ValueError("Bad column index")
		return val

class MatchedFilesListCtrl(AbstractFileInfoListCtrl):
	def get_column_names(self):
		return ("Old", "New", "Name Changed")

	def get_column_widths(self):
		return (200, 200, 40)

	def get_text_val(self, item_idx, col, mapped=True):
		if mapped:
			index = self.itemIndexMap[item_idx]
		else:
			index = item_idx
		data = self.items[index]
		if col == 0:
			val = data[0].get_full_fn()
		elif col == 1:
			val = data[1].get_full_fn()
		elif col == 2:
			is_name_changed = data[0].get_fn() != data[1].get_fn()
			val = ""
			if is_name_changed:
				val = "Yes"
		else:
			raise ValueError("Bad column index")
		return val

class UpdatedFilesListCtrl(AbstractFileInfoListCtrl):
	def get_column_names(self):
		return ("Old", "New", "More Recent")

	def get_column_widths(self):
		return (200, 200, 40)

	def get_text_val(self, item_idx, col, mapped=True):
		if mapped:
			index = self.itemIndexMap[item_idx]
		else:
			index = item_idx
		data = self.items[index]
		if col == 0:
			val = data[0].get_full_fn()
		elif col == 1:
			val = data[1].get_full_fn()
		elif col == 2:
			is_newer_more_recent = data[0].get_mtime() < data[1].get_mtime()
			val = "No"
			if is_newer_more_recent:
				val = "Yes"
		else:
			raise ValueError("Bad column index")
		return val

	def set_items(self, items):
		filtered = []
		for old_file_info in items:
			maybe_list = old_file_info.get_maybe_updated()
			if maybe_list is not None:
				for new_file_info in maybe_list:
					filtered.append((old_file_info, new_file_info))
		self.items = filtered
		self.SetItemCount(len(filtered))
		self.itemIndexMap = [x for x in range(len(filtered))]
class MovedEmApp(wx.App):
	def OnInit(self):
		self.frame = MainWindow(None, wx.ID_ANY, "")
		self.SetTopWindow(self.frame)
		self.frame.Show()
		return True

# end of class MovedEmApp

class MovedEmThread(threading.Thread):
	def __init__(self, callback, args):
		super().__init__()
		self.callback = callback
		self.errorCount = 0
		self.args = args
		self.stopping = False
		self.done = False

	def run(self):
		self.move_checker = movedem.MoveChecker(self.args.dir_old, self.args.dir_new, callback=self.callback, args=self.args)
		if self.args.debug:
			self.move_checker.logger.setLevel(logging.DEBUG)
		self.move_checker.do_checks()
		self.done = True

	def stop(self):
		self.move_checker.stop_processing()
		self.stopping = True
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
	app = MovedEmApp(0)
	app.MainLoop()
	pass