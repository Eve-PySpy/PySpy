# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian <wrusssian@gmail.com>***************
'''Very simple wxpython GUI with 1 frame, using persistent properties.'''
# **********************************************************************
import logging
import os
import sys
import time

import webbrowser
import wx
import wx.lib.agw.persist as pm

import config
import statusmsg
# **********************************************************************
Logger = logging.getLogger(__name__)
# Example call: Logger.info("Something badhappened", exc_info=True) ****


class Frame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.STAY_ON_TOP | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        # wx.Frame.__init__(self, id=wx.ID_ANY, name='', style=wx.NO_BORDER)
        self.SetName("Main Window")

        # Define the main list control
        self.list = wx.ListCtrl(self, wx.ID_ANY, style=wx.BORDER_NONE |
            wx.FULL_REPAINT_ON_RESIZE | wx.LC_HRULES | wx.LC_REPORT |
            wx.LC_SINGLE_SEL | wx.LC_VRULES
            )
        self.list.SetName("Output List")

        # Ensure that Persistence Manager saves window location on close
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Bind double click on list item to zKill link.
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.go_to_zKill, self.list)

        # Allow to change window transparency using this slider.
        self.alpha_slider = wx.Slider(self, wx.ID_ANY, 230, 50, 255)
        self.alpha_slider.SetName("Transparency_Slider")
        self.Bind(wx.EVT_SLIDER, self.set_transparency)

        # The status label shows various info and error messages.
        self.status_label = wx.StaticText(
            self,
            wx.ID_ANY,
            "To start analysis, please copy EVE Local to clipboard.",
            style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_END
            )
        self.status_label.SetName("Status_Bar")

        # First set default properties, then restore persistence if any
        self.__set_properties()

        # Set up Persistence Manager
        self._persistMgr = pm.PersistenceManager.Get()
        self._persistMgr.SetPersistenceFile(config.GUI_CFG_FILE)
        if not self._persistMgr.RegisterAndRestoreAll(self):
            Logger.info(
                "Could not access or create configuration file at:" +
                config.GUI_CFG_FILE,
                exc_info=True
                )

        self.set_transparency()  # Set transparency based off restored slider
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("PySpy v0.1")
        self.SetTransparent(230)
        self.SetSize((605, 400))
        self.list.AppendColumn("ID", format=wx.LIST_FORMAT_LEFT, width=0)
        self.list.AppendColumn("Character", format=wx.LIST_FORMAT_LEFT, width=125)
        self.list.AppendColumn("Corporation", format=wx.LIST_FORMAT_LEFT, width=145)
        self.list.AppendColumn("Alliance", format=wx.LIST_FORMAT_LEFT, width=210)
        self.list.AppendColumn("K - B - H", format=wx.LIST_FORMAT_CENTER, width=90)
        self.alpha_slider.SetMinSize((100, 20))
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(config.ICON_FILE, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

    def __do_layout(self):
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_bottom = wx.BoxSizer(wx.HORIZONTAL)
        sizer_main.Add(self.list, 1, wx.EXPAND, 0)
        sizer_bottom.Add(self.status_label, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        static_line = wx.StaticLine(self, wx.ID_ANY, style=wx.LI_VERTICAL)
        sizer_bottom.Add(static_line, 0, wx.EXPAND, 0)
        sizer_bottom.Add(self.alpha_slider, 0, wx.ALIGN_RIGHT, 0)
        sizer_main.Add(sizer_bottom, 0, wx.ALIGN_BOTTOM | wx.ALL | wx.EXPAND, 1)
        self.SetSizer(sizer_main)
        self.Layout()

    def update_list(self, outlist, start_time):
        self.list.DeleteAllItems()
        for r in outlist:
            id = r[0]
            name = r[1]
            corp = r[2]
            alliance = str(r[3]) + " (" + str(r[4]) + ")" if r[3] is not None else "-"
            zkill = str(r[5]) + " - " + str(r[6]) + " - " + str(r[7]) if r[5] is not None else "n.a."
            out = [id, name, corp, alliance, zkill]
            self.list.Append(out)
            if r[6] is not None and (r[6] > 0 or r[7] > 0):  # Highlight BLOPS killer & HIC pilots.
                self.list.SetItemBackgroundColour(
                    self.list.ItemCount - 1,
                    wx.Colour(255, 189, 90)
                    )
        duration = round(time.time() - start_time, 1)
        statusmsg.push_status(
            str(len(outlist)) +
            " characters analysed in " + str(duration) +
            " seconds. Double click character to go to zKillboard."
            )

    def update_statusbar(self, msg):
        if isinstance(msg, str):
            self.status_label.SetLabel(msg)
            # self.sizer_bottom.Layout()
            self.Layout()

    def go_to_zKill(self, event):
        webbrowser.open_new_tab(
            "https://zkillboard.com/character/" +
            str(event.GetText())
            )

    def set_transparency(self, event=None):
        alpha = self.alpha_slider.GetValue()
        self.SetTransparent(alpha)
        self.Layout()

    def OnClose(self, event):
        self._persistMgr.SaveAndUnregister()
        event.Skip()


class App(wx.App):
    def OnInit(self):
        self.PySpy = Frame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.PySpy)
        self.PySpy.Show()
        return True
