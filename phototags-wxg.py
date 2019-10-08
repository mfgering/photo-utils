#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.4 on Mon Oct  7 16:30:26 2019
#

import phototags
import logging, os, sys, threading, wx
import wx.grid as gridlib

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class MainWindow(wx.Frame):
	def __init__(self, *args, **kwds):
		# begin wxGlade: MainWindow.__init__
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
		wx.Frame.__init__(self, *args, **kwds)
		self.SetSize((694, 609))
		self.SetTitle("frame")
		
		self.frame_statusbar = self.CreateStatusBar(1)
		self.frame_statusbar.SetStatusWidths([-1])
		# statusbar fields
		frame_statusbar_fields = ["frame_statusbar"]
		for i in range(len(frame_statusbar_fields)):
			self.frame_statusbar.SetStatusText(frame_statusbar_fields[i], i)
		
		sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		
		self.notebook_1 = wx.Notebook(self, wx.ID_ANY, style=wx.NB_LEFT)
		sizer_2.Add(self.notebook_1, 1, wx.EXPAND, 0)
		
		self.options_page = wx.Panel(self.notebook_1, wx.ID_ANY)
		self.options_page.SetToolTip("Show/edit processing options")
		self.notebook_1.AddPage(self.options_page, "Options")
		
		sizer_3 = wx.BoxSizer(wx.VERTICAL)
		
		self.checkbox_check_allowed = wx.CheckBox(self.options_page, wx.ID_ANY, "Check allowed")
		self.checkbox_check_allowed.SetValue(1)
		self.checkbox_check_allowed.arg_name = "check_allowed"
		sizer_3.Add(self.checkbox_check_allowed, 0, wx.LEFT, 15)
		
		self.checkbox_check_required = wx.CheckBox(self.options_page, wx.ID_ANY, "Check required")
		self.checkbox_check_required.SetValue(1)
		self.checkbox_check_required.arg_name = "check_required"
		sizer_3.Add(self.checkbox_check_required, 0, wx.LEFT, 15)
		
		self.checkbox_check_frequency = wx.CheckBox(self.options_page, wx.ID_ANY, "Check frequency")
		self.checkbox_check_frequency.arg_name = "frequency"
		sizer_3.Add(self.checkbox_check_frequency, 0, wx.LEFT, 15)
		
		self.checkbox_file_tags = wx.CheckBox(self.options_page, wx.ID_ANY, "File tags")
		self.checkbox_file_tags.SetValue(1)
		self.checkbox_file_tags.arg_name = "print_file_tags"
		sizer_3.Add(self.checkbox_file_tags, 0, wx.LEFT, 15)
		
		sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_3.Add(sizer_5, 0, wx.LEFT, 15)
		
		self.text_ctrl_max_files = wx.TextCtrl(self.options_page, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB)
		self.text_ctrl_max_files.SetToolTip("Maximum number of files to process (or 'All')")
		self.text_ctrl_max_files.arg_name = "max_files"
		sizer_5.Add(self.text_ctrl_max_files, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		
		static_text_max_files = wx.StaticText(self.options_page, wx.ID_ANY, "Max files")
		sizer_5.Add(static_text_max_files, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
		
		sizer_6 = wx.StaticBoxSizer(wx.StaticBox(self.options_page, wx.ID_ANY, "Target"), wx.HORIZONTAL)
		sizer_3.Add(sizer_6, 0, wx.EXPAND | wx.LEFT, 15)
		
		self.text_ctrl_target = wx.TextCtrl(self.options_page, wx.ID_ANY, "")
		self.text_ctrl_target.arg_name = "targ_arg"
		sizer_6.Add(self.text_ctrl_target, 1, wx.EXPAND, 0)
		
		self.button_select_target = wx.Button(self.options_page, wx.ID_ANY, "Select")
		sizer_6.Add(self.button_select_target, 0, wx.LEFT, 15)
		
		sizer_3.Add((20, 20), 0, 0, 0)
		
		sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_3.Add(sizer_4, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
		
		self.apply_options_button = wx.Button(self.options_page, wx.ID_ANY, "Apply")
		sizer_4.Add(self.apply_options_button, 0, wx.RIGHT, 10)
		
		self.revert_options_button = wx.Button(self.options_page, wx.ID_ANY, "Revert")
		sizer_4.Add(self.revert_options_button, 0, wx.RIGHT, 10)
		
		sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_3.Add(sizer_7, 0, wx.LEFT, 15)
		
		self.button_start = wx.Button(self.options_page, wx.ID_ANY, "Start")
		sizer_7.Add(self.button_start, 0, wx.RIGHT, 10)
		
		self.button_stop = wx.Button(self.options_page, wx.ID_ANY, "Stop")
		sizer_7.Add(self.button_stop, 0, 0, 0)
		
		self.notebook_1_Tags = wx.Panel(self.notebook_1, wx.ID_ANY)
		self.notebook_1_Tags.SetToolTip("Show tags used by individual files")
		self.notebook_1.AddPage(self.notebook_1_Tags, "Tags")
		
		self.notebook_1_Missing = wx.Panel(self.notebook_1, wx.ID_ANY)
		self.notebook_1.AddPage(self.notebook_1_Missing, "Missing")
		
		self.notebook_1_Disallowed = wx.Panel(self.notebook_1, wx.ID_ANY)
		self.notebook_1.AddPage(self.notebook_1_Disallowed, "Disallowed")
		
		self.notebook_1_Frequency = wx.Panel(self.notebook_1, wx.ID_ANY)
		self.notebook_1.AddPage(self.notebook_1_Frequency, "Frequency")
		
		self.notebook_1_logs = wx.ScrolledWindow(self.notebook_1, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.notebook_1_logs.Enable(False)
		self.notebook_1_logs.SetScrollRate(10, 10)
		self.notebook_1.AddPage(self.notebook_1_logs, "Logs")
		
		sizer_1 = wx.BoxSizer(wx.VERTICAL)
		
		self.log_text_ctrl = wx.TextCtrl(self.notebook_1_logs, wx.ID_ANY, "", style=wx.HSCROLL | wx.TE_MULTILINE | wx.TE_READONLY)
		sizer_1.Add(self.log_text_ctrl, 1, wx.ALL | wx.EXPAND, 0)
		
		self.notebook_1_logs.SetSizer(sizer_1)
		
		self.options_page.SetSizer(sizer_3)
		
		self.SetSizer(sizer_2)
		
		self.Layout()

		self.Bind(wx.EVT_CHECKBOX, self.on_options_event, self.checkbox_check_allowed)
		self.Bind(wx.EVT_CHECKBOX, self.on_options_event, self.checkbox_check_required)
		self.Bind(wx.EVT_CHECKBOX, self.on_options_event, self.checkbox_check_frequency)
		self.Bind(wx.EVT_CHECKBOX, self.on_options_event, self.checkbox_file_tags)
		self.Bind(wx.EVT_TEXT_ENTER, self.on_options_event, self.text_ctrl_max_files)
		self.Bind(wx.EVT_BUTTON, self.on_apply_options, self.apply_options_button)
		self.Bind(wx.EVT_BUTTON, self.on_revert_options, self.revert_options_button)
		self.Bind(wx.EVT_BUTTON, self.on_start_button, self.button_start)
		self.Bind(wx.EVT_BUTTON, self.on_stop_button, self.button_stop)
		# end wxGlade
		try:
			# redirect text here
			redir=RedirectText(self.log_text_ctrl, threading.current_thread().ident)
			sys.stdout = redir
			sys.stderr = redir
			
			self.args = self.parseArgs()
			self.update_options()
			self.target = self.args.targ_arg
			self.config = phototags.PhotoTagsConfig()
			self.config.read_config(self.args.config)

			self.tag_info = []
			#self.options_panel.set_options(self.args)
			#self.setButtonStates()
		except Exception as exc:
			self.GetStatusBar().SetStatusText("Error: "+str(exc))
		print("App starting")


	def __set_properties(self):
		pass #TODO: FIX THIS

	def __do_layout(self):
		pass #TODO: FIX THIS

	def on_target(self, event):  # wxGlade: MainWindow.<event_handler>
		print("Event handler 'on_target' not implemented!")
		event.Skip()

	def on_tags(self, event):  # wxGlade: MainWindow.<event_handler>
		print("Event handler 'on_tags' not implemented!")
		event.Skip()

	def on_log(self, event):  # wxGlade: MainWindow.<event_handler>
		print("Event handler 'on_log' not implemented!")
		event.Skip()

	def parseArgs(self):
		parser = phototags.initArgParser()
		parser.add_argument('--target', default=".", dest='targ_arg', help="File or directory to check")
		return parser.parse_args()

	def on_apply_options(self, event):  # wxGlade: MainWindow.<event_handler>
		page = self.options_page.GetChildren()
		for i in page:
			if hasattr(i, "arg_name"):
				arg_name = getattr(i, "arg_name")
				if arg_name == "max_files":
					val = -1
					val_str = i.GetValue().strip()
					if len(val_str) > 0 and val_str.lower() != "all":
						try:
							val = int(val_str)
						except Exception as exc:
							logging.getLogger().exception(exc)
							i.SetValue("All")
					setattr(self.args, arg_name,val)
				else:
					setattr(self.args, arg_name, bool(i.GetValue()))
		self.apply_options_button.Enable(False)
		self.revert_options_button.Enable(False)

	def on_revert_options(self, event):  # wxGlade: MainWindow.<event_handler>
		self.update_options()
		
	def on_options_event(self, event):  # wxGlade: MainWindow.<event_handler>
		self.apply_options_button.Enable(True)
		self.revert_options_button.Enable(True)

	def update_options(self):
		page = self.options_page.GetChildren()
		for i in page:
			if hasattr(i, "arg_name"):
				arg_name = getattr(i, "arg_name")
				arg_value = getattr(self.args, arg_name)
				if arg_name == "max_files":
					str_value = str(arg_value)
					if arg_value < 0:
						str_value = "All"
					i.SetValue(str_value)
				else:
					i.SetValue(arg_value)
		self.apply_options_button.Enable(False)
		self.revert_options_button.Enable(False)
	def on_start_button(self, event):  # wxGlade: MainWindow.<event_handler>
		print("Event handler 'on_start_button' not implemented!")
		event.Skip()
	def on_stop_button(self, event):  # wxGlade: MainWindow.<event_handler>
		print("Event handler 'on_stop_button' not implemented!")
		event.Skip()
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
					tags_allowed=self.config.tags_allowed, tags_required=self.config.tags_required)
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
