#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.9pre on Mon Oct 21 09:11:54 2019
#

import wx
import wx.grid

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class ImageDedupFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: ImageDedupFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((400, 300))
        self.SetTitle("frame")
        
        self.frame_statusbar = self.CreateStatusBar(1)
        self.frame_statusbar.SetStatusWidths([-1])
        # statusbar fields
        frame_statusbar_fields = ["frame_statusbar"]
        for i in range(len(frame_statusbar_fields)):
            self.frame_statusbar.SetStatusText(frame_statusbar_fields[i], i)
        
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        
        self.notebook_1 = wx.Notebook(self, wx.ID_ANY, style=wx.NB_BOTTOM)
        sizer_1.Add(self.notebook_1, 1, wx.ALL | wx.EXPAND, 5)
        
        self.options_page = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.options_page.SetToolTip("Show/edit processing options")
        self.notebook_1.AddPage(self.options_page, "Options")
        
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        
        sizer_10 = wx.StaticBoxSizer(wx.StaticBox(self.options_page, wx.ID_ANY, "Options"), wx.VERTICAL)
        sizer_3.Add(sizer_10, 0, wx.ALL | wx.EXPAND, 15)
        
        sizer_11 = wx.BoxSizer(wx.VERTICAL)
        sizer_10.Add(sizer_11, 1, wx.EXPAND | wx.LEFT, 15)
        
        self.checkbox_replace_encodings = wx.CheckBox(self.options_page, wx.ID_ANY, "Replace encodings")
        self.checkbox_replace_encodings.SetValue(1)
        sizer_11.Add(self.checkbox_replace_encodings, 0, wx.TOP, 5)
        
        sizer_11.Add((0, 0), 0, 0, 0)
        
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11.Add(sizer_4, 1, wx.EXPAND, 0)
        
        self.text_dist_thresh = wx.TextCtrl(self.options_page, wx.ID_ANY, "")
        sizer_4.Add(self.text_dist_thresh, 0, wx.TOP, 5)
        
        static_text_dist_thresh = wx.StaticText(self.options_page, wx.ID_ANY, "Distance threshold")
        sizer_4.Add(static_text_dist_thresh, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.TOP, 5)
        
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10.Add(sizer_5, 0, wx.LEFT, 15)
        
        self.text_ctrl_max_files = wx.TextCtrl(self.options_page, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER | wx.TE_PROCESS_TAB)
        self.text_ctrl_max_files.SetToolTip("Maximum number of files to process (or 'All')")
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
        
        sizer_7 = wx.StaticBoxSizer(wx.StaticBox(self.options_page, wx.ID_ANY, "Processing"), wx.HORIZONTAL)
        sizer_3.Add(sizer_7, 0, wx.ALL, 15)
        
        self.button_start = wx.Button(self.options_page, wx.ID_ANY, "Start")
        sizer_7.Add(self.button_start, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        
        self.button_stop = wx.Button(self.options_page, wx.ID_ANY, "Stop")
        self.button_stop.Enable(False)
        sizer_7.Add(self.button_stop, 0, wx.RIGHT | wx.TOP, 10)
        
        self.notebook_1_dups = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.notebook_1_dups.SetToolTip("Show duplicates")
        self.notebook_1.AddPage(self.notebook_1_dups, "Dups")
        
        sizer_8 = wx.BoxSizer(wx.VERTICAL)
        
        self.static_text_tags_header = wx.StaticText(self.notebook_1_dups, wx.ID_ANY, "Not yet set\n", style=wx.ALIGN_CENTER)
        self.static_text_tags_header.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_8.Add(self.static_text_tags_header, 0, wx.ALL, 15)
        
        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8.Add(sizer_9, 1, wx.EXPAND, 0)
        
        self.grid_tags = wx.grid.Grid(self.notebook_1_dups, wx.ID_ANY, size=(1, 1))
        self.grid_tags.CreateGrid(0, 2)
        self.grid_tags.EnableEditing(0)
        self.grid_tags.EnableDragRowSize(0)
        self.grid_tags.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid_tags.SetColLabelValue(0, "Filename")
        self.grid_tags.SetColLabelValue(1, "All Tags")
        sizer_9.Add(self.grid_tags, 1, wx.ALL | wx.EXPAND, 15)
        
        self.notebook_1_logs = wx.ScrolledWindow(self.notebook_1, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.notebook_1_logs.SetScrollRate(10, 10)
        self.notebook_1.AddPage(self.notebook_1_logs, "Logs")
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        
        self.log_text_ctrl = wx.TextCtrl(self.notebook_1_logs, wx.ID_ANY, "", style=wx.TE_BESTWRAP | wx.TE_MULTILINE | wx.TE_READONLY)
        sizer_2.Add(self.log_text_ctrl, 1, wx.ALL | wx.EXPAND, 15)
        
        self.notebook_1_logs.SetSizer(sizer_2)
        
        self.notebook_1_dups.SetSizer(sizer_8)
        
        self.options_page.SetSizer(sizer_3)
        
        self.SetSizer(sizer_1)
        
        self.Layout()

        self.Bind(wx.EVT_CHECKBOX, self.on_options_event, self.checkbox_replace_encodings)
        self.Bind(wx.EVT_TEXT, self.on_options_event, self.text_ctrl_max_files)
        self.Bind(wx.EVT_TEXT, self.on_options_event, self.text_ctrl_target)
        self.Bind(wx.EVT_BUTTON, self.on_target_select, self.button_select_target)
        self.Bind(wx.EVT_BUTTON, self.on_start_button, self.button_start)
        self.Bind(wx.EVT_BUTTON, self.on_stop_button, self.button_stop)
        # end wxGlade

    def on_options_event(self, event):  # wxGlade: ImageDedupFrame.<event_handler>
        print("Event handler 'on_options_event' not implemented!")
        event.Skip()

    def on_target_select(self, event):  # wxGlade: ImageDedupFrame.<event_handler>
        print("Event handler 'on_target_select' not implemented!")
        event.Skip()

    def on_start_button(self, event):  # wxGlade: ImageDedupFrame.<event_handler>
        print("Event handler 'on_start_button' not implemented!")
        event.Skip()

    def on_stop_button(self, event):  # wxGlade: ImageDedupFrame.<event_handler>
        print("Event handler 'on_stop_button' not implemented!")
        event.Skip()

# end of class ImageDedupFrame

class MyApp(wx.App):
    def OnInit(self):
        self.frame = ImageDedupFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()