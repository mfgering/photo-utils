#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.9pre on Wed Nov 27 11:39:19 2019
#

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class MainWindow(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MainWindow.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((400, 300))
        self.SetTitle("Moved Some Files -- Let's Check 'Em")
        
        self.frame_statusbar = self.CreateStatusBar(1)
        self.frame_statusbar.SetStatusWidths([-1])
        # statusbar fields
        frame_statusbar_fields = ["frame_statusbar"]
        for i in range(len(frame_statusbar_fields)):
            self.frame_statusbar.SetStatusText(frame_statusbar_fields[i], i)
        
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        
        sizer_1.Add((0, 0), 0, 0, 0)
        
        self.SetSizer(sizer_1)
        
        self.Layout()
        # end wxGlade

# end of class MainWindow

class MovedEmApp(wx.App):
    def OnInit(self):
        self.frame = MainWindow(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

# end of class MovedEmApp

if __name__ == "__main__":
    app = MovedEmApp(0)
    app.MainLoop()
