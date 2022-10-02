# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian
# Github: <https://github.com/Eve-PySpy/PySpy>**********************
''' Dialog to view and remove entities from PySpy's list of highlighted
characters, corporations and alliances.
'''
# **********************************************************************
import logging

import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

import config
import sortarray
import statusmsg
# cSpell Checker - Correct Words****************************************
# // cSpell:words russsian, ccp's, pyperclip, chkversion, clpbd, gui
# **********************************************************************
Logger = logging.getLogger(__name__)
# Example call: Logger.info("Something badhappened", exc_info=True) ****


class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT |
        wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)


class HighlightDialog(wx.Frame):
    def __init__(self, parent, *args, **kwds):
        kwds["style"] = (kwds.get("style", 0) | wx.CAPTION | wx.CLIP_CHILDREN |
            wx.CLOSE_BOX | wx.FRAME_FLOAT_ON_PARENT | wx.RESIZE_BORDER)
        wx.Frame.__init__(self, parent, *args, **kwds)

        self.Font = self.Font.Scaled(config.OPTIONS_OBJECT.Get("FontScale", 1))
        self.SetName("HighlightDialog")
        self.SetSize((400, 300))

        self.highlightList = CheckListCtrl(self)
        self.highlightList.InsertColumn(0, 'Name', width=180)
        self.highlightList.InsertColumn(1, 'ID', width=0)
        self.highlightList.InsertColumn(2, 'Type')
        self.buttonPanel = wx.Panel(self, wx.ID_ANY)
        self.appBtn = wx.Button(self.buttonPanel, wx.ID_OK, "Delete Selected Entries")
        self.cnclBtn = wx.Button(self.buttonPanel, wx.ID_CANCEL, "Cancel Changes")

        self.Bind(wx.EVT_BUTTON, self.OnApply, id=self.appBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=self.cnclBtn.GetId())
        self.Bind(wx.EVT_CHAR_HOOK, self.OnHook)

        self.highlighted_entities = config.OPTIONS_OBJECT.Get("highlightedList", default=[])
        self._populateList()

        self.__set_properties()
        self.__do_layout()

        if config.OPTIONS_OBJECT.Get("StayOnTop", True):
            self.Parent.ToggleWindowStyle(wx.STAY_ON_TOP)
        self.ToggleWindowStyle(wx.STAY_ON_TOP)

    def __set_properties(self):
        self.SetTitle("Review Highlighted Entities")
        # Colour Scheme Dictionaries
        self.dark_dict = config.DARK_MODE
        self.normal_dict = config.NORMAL_MODE

        # Colour Scheme
        if not config.OPTIONS_OBJECT.Get("DarkMode", False):
            self.bg_colour = self.normal_dict["BG"]
            self.txt_colour = self.normal_dict["TXT"]
            self.lne_colour = self.normal_dict["LNE"]
            self.hl1_colour = self.normal_dict["HL1"]
        else:
            self.bg_colour = self.dark_dict["BG"]
            self.txt_colour = self.dark_dict["TXT"]
            self.lne_colour = self.dark_dict["LNE"]
            self.hl1_colour = self.dark_dict["HL1"]

        # Set default colors
        self.SetBackgroundColour(self.bg_colour)
        self.SetForegroundColour(self.txt_colour)
        self.highlightList.SetBackgroundColour(self.bg_colour)
        self.highlightList.SetForegroundColour(self.txt_colour)

        # Window icon
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(config.ICON_FILE, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

    def __do_layout(self):
        main = wx.BoxSizer(wx.VERTICAL)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        instrLbl = wx.StaticText(self, wx.ID_ANY, "Select entities to be removed from highlight list:", style=wx.ALIGN_LEFT)
        main.Add(instrLbl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        main.Add(self.highlightList, 1, wx.ALL | wx.EXPAND, 10)
        buttonSizer.Add(self.appBtn, 1, wx.RIGHT, 5)
        buttonSizer.Add(self.cnclBtn, 1, wx.LEFT, 5)
        self.buttonPanel.SetSizer(buttonSizer)
        if config.wx_minor < 1:
            main.Add(self.buttonPanel, 0, wx.ALIGN_BOTTOM | wx.BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        else:
            main.Add(self.buttonPanel, 0, wx.BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        self.SetSizer(main)
        self.Layout()
        self.Centre()

    def _populateList(self):
        idx = 0
        if self.highlighted_entities == []:
            return
        if len(self.highlighted_entities) > 1:
            self.highlighted_entities = sortarray.sort_array(self.highlighted_entities, 2, 1)
        for i in self.highlighted_entities:
            index = self.highlightList.InsertItem(idx, i[1])
            self.highlightList.SetItem(index, 1, str(i[0]))
            self.highlightList.SetItem(index, 2, i[2])
            idx += 1

    def OnHook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.OnCancel(event)
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.OnApply(event)
        else:
            event.Skip()

    def OnApply(self, event):
        num = self.highlightList.GetItemCount()
        for i in range(num):
            if self.highlightList.IsChecked(i):
                id = int(self.highlightList.GetItemText(i, 1))
                n = 0
                for r in self.highlighted_entities:
                    if r[0] == id:
                        del self.highlighted_entities[n]
                    n += 1
        config.OPTIONS_OBJECT.Set("highlightedList", self.highlighted_entities)
        self.Parent.updateList(config.OPTIONS_OBJECT.Get("outlist"))
        self.Close()

    def OnCancel(self, event):
        if config.OPTIONS_OBJECT.Get("StayOnTop", True):
            self.Parent.ToggleWindowStyle(wx.STAY_ON_TOP)
        self.Close()


def showHighlightDialog(parent, evt=None):
    app = wx.App(False)
    frame = HighlightDialog(parent=parent)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
