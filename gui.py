# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian
# Github: <https://github.com/WhiteRusssian/PySpy>**********************
'''Simple wxpython GUI with 1 frame, using persistent properties.'''
# **********************************************************************
import logging
import os
import sys
import time
import webbrowser

import wx
import wx.lib.agw.persist as pm

import aboutdialog
import config
import statusmsg
# cSpell Checker - Correct Words****************************************
# // cSpell:words wrusssian, wxpython, HRULES, VRULES, ELLIPSIZE, zkill,
# // cSpell:words blops, Unregister, russsian, chkversion, posix,
# // cSpell:words Gallente, Minmatar, Amarr, Caldari, ontop
# **********************************************************************
Logger = logging.getLogger(__name__)
# Example call: Logger.info("Something badhappened", exc_info=True) ****


class Frame(wx.Frame):
    def __init__(self, *args, **kwds):

        # Persistent Options
        self.options = config.OPTIONS_OBJECT

        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetName("Main Window")

        # Set stay on-top unless user deactivated it
        if self.options.Get("StayOnTop", True):
            self.ToggleWindowStyle(wx.STAY_ON_TOP)

        # Define the menu bar and menu items
        self.menubar = wx.MenuBar()
        self.menubar.SetName("Menubar")
        if os.name == "nt":  # For Windows
            self.file_menu = wx.Menu()
            self.file_about = self.file_menu.Append(wx.ID_ANY, 'About')
            self.file_menu.Bind(wx.EVT_MENU, aboutdialog.OnAboutBox, self.file_about)
            self.file_quit = self.file_menu.Append(wx.ID_ANY, 'Quit PySpy')
            self.file_menu.Bind(wx.EVT_MENU, self.OnQuit, self.file_quit)
            self.menubar.Append(self.file_menu, 'File')
        if os.name == "posix":  # For macOS
            self.help_menu = wx.Menu()
            self.help_about = self.help_menu.Append(wx.ID_ANY, 'About')
            self.help_menu.Bind(wx.EVT_MENU, aboutdialog.OnAboutBox, self.help_about)
            self.menubar.Append(self.help_menu, 'Help')

        # View menu is platform independent
        self.view_menu = wx.Menu()

        # Toggle highlighting of BLOPS kills and HIC losses
        self.hl_blops = self.view_menu.AppendCheckItem(
            wx.ID_ANY, 'Highlight BLOPS Kills and HIC Losses'
            )
        self.view_menu.Bind(wx.EVT_MENU, self.toggleHlBlops, self.hl_blops)

        self.view_menu.AppendSeparator()

        # Show / hide columns
        self.show_corp = self.view_menu.AppendCheckItem(wx.ID_ANY, 'Show Corporation')
        self.view_menu.Bind(wx.EVT_MENU, self.toggleViewCorp, self.show_corp)

        self.show_alliance = self.view_menu.AppendCheckItem(wx.ID_ANY, 'Show Alliance')
        self.view_menu.Bind(wx.EVT_MENU, self.toggleViewAlliance, self.show_alliance)

        self.show_faction = self.view_menu.AppendCheckItem(wx.ID_ANY, 'Show Faction')
        self.view_menu.Bind(wx.EVT_MENU, self.toggleViewFaction, self.show_faction)

        self.view_menu.AppendSeparator()

        # Ignore Factions submenu for view menu
        self.view_sub_menu = wx.Menu()
        self.view_menu.Append(wx.ID_ANY, "Ignore Factions", self.view_sub_menu)

        self.ignore_galmin = self.view_sub_menu.AppendRadioItem(wx.ID_ANY, "Gallente / Minmatar")
        self.view_sub_menu.Bind(wx.EVT_MENU, self.toggleIgnoreFactions, self.ignore_galmin)

        self.ignore_amacal = self.view_sub_menu.AppendRadioItem(wx.ID_ANY, "Amarr / Caldari")
        self.view_sub_menu.Bind(wx.EVT_MENU, self.toggleIgnoreFactions, self.ignore_amacal)

        self.ignore_none = self.view_sub_menu.AppendRadioItem(wx.ID_ANY, "None")
        self.view_sub_menu.Bind(wx.EVT_MENU, self.toggleIgnoreFactions, self.ignore_none)

        self.view_menu.AppendSeparator()

        # Toggle Stay on-top
        self.stay_ontop = self.view_menu.AppendCheckItem(
            wx.ID_ANY, 'Stay on-top'
            )
        self.view_menu.Bind(wx.EVT_MENU, self.toggleStayOnTop, self.stay_ontop)

        self.menubar.Append(self.view_menu, 'View')

        # Menu Defaults, saved with optstore.PersistentOptions
        self.hl_blops.Check(self.options.Get("HlBlops", True))
        self.show_corp.Check(self.options.Get("ShowCorp", True))
        self.show_alliance.Check(self.options.Get("ShowAlliance", True))
        self.show_faction.Check(self.options.Get("ShowFaction", True))
        self.ignore_galmin.Check(self.options.Get("HlGalMin", False))
        self.ignore_amacal.Check(self.options.Get("HlAmaCal", False))
        self.ignore_none.Check(self.options.Get("HlNone", True))
        self.stay_ontop.Check(self.options.Get("StayOnTop", True))

        # Define the main list control
        self.list = wx.ListCtrl(self, wx.ID_ANY, style=wx.BORDER_NONE |
            wx.FULL_REPAINT_ON_RESIZE | wx.LC_HRULES | wx.LC_REPORT |
            wx.LC_SINGLE_SEL | wx.LC_VRULES
            )
        self.list.SetName("Output List")

        # Ensure that Persistence Manager saves window location on close
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Bind double click on list item to zKill link.
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.goToZKill, self.list)

        # Allow to change window transparency using this slider.
        self.alpha_slider = wx.Slider(self, wx.ID_ANY, 250, 50, 255)
        self.alpha_slider.SetName("Transparency_Slider")
        self.Bind(wx.EVT_SLIDER, self.setTransparency)

        # The status label shows various info and error messages.
        self.status_label = wx.StaticText(
            self,
            wx.ID_ANY,
            "Please copy some EVE character names to clipboard...",
            style=wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_END
            )
        self.status_label.SetName("Status_Bar")

        # First set default properties, then restore persistence if any
        self.__set_properties()

        # Set up Persistence Manager
        self._persistMgr = pm.PersistenceManager.Get()
        self._persistMgr.SetPersistenceFile(config.GUI_CFG_FILE)
        self._persistMgr.RegisterAndRestoreAll(self)

        self.setTransparency()  # Set transparency based off restored slider
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle(config.GUI_TITLE)
        self.SetSize((625, 400))
        self.SetMenuBar(self.menubar)
        self.list.AppendColumn("ID", format=wx.LIST_FORMAT_LEFT, width=0)
        self.list.AppendColumn("FactionID", format=wx.LIST_FORMAT_LEFT, width=0)
        self.list.AppendColumn("Character", format=wx.LIST_FORMAT_LEFT, width=115)
        self.lc_corp = self.list.AppendColumn("Corporation", format=wx.LIST_FORMAT_LEFT, width=115)
        self.lc_alliance = self.list.AppendColumn("Alliance", format=wx.LIST_FORMAT_LEFT, width=175)
        self.lc_faction = self.list.AppendColumn("Faction", format=wx.LIST_FORMAT_LEFT, width=60)
        self.list.AppendColumn("Last Wk", format=wx.LIST_FORMAT_CENTER, width=50)
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

    def updateList(self, outlist, duration=None):
        # If updateList() gets called before outlist has been provided, do nothing
        if outlist is None:
            return
        self.options.Set("outlist", outlist)
        hl_blops = self.options.Get("HlBlops", True)
        self.list.DeleteAllItems()
        for r in outlist:

            # Schema depending on output_list() in analyze.py
            id = r[0]
            faction_id = r[1]
            name = r[2]
            corp = r[3]
            alliance = str(r[4]) + " (" + str(r[6]) + ")" if r[4] is not None else "-"
            faction = r[5] if r[5] is not None else "-"
            week_kills = r[7]
            zkill = str(r[8]) + " - " + str(r[9]) + " - " + str(r[10]) if r[8] is not None else "n.a."
            out = [id, faction_id, name, corp, alliance, faction, week_kills, zkill]

            # Check if character belongs to a faction that should be ignored
            if faction_id != 0:
                if config.IGNORED_FACTIONS == 2 and faction_id % 2 == 0:
                    continue
                if config.IGNORED_FACTIONS == 1 and faction_id % 2 != 0:
                    continue

            self.list.Append(out)

            if hl_blops and r[7] is not None and (r[9] > 0 or r[10] > 0):  # Highlight BLOPS killer & HIC pilots.
                self.list.SetItemBackgroundColour(
                    self.list.ItemCount - 1,
                    wx.Colour(255, 189, 90)
                    )
        if duration is not None:
            statusmsg.push_status(
                str(len(outlist)) +
                " characters analysed in " + str(duration) +
                " seconds. Double click character to go to zKillboard."
                )

    def updateStatusbar(self, msg):
        '''Gets called by push_status() in statusmsg.py.'''
        if isinstance(msg, str):
            self.status_label.SetLabel(msg)
            self.Layout()

    def goToZKill(self, event):
        webbrowser.open_new_tab(
            "https://zkillboard.com/character/" +
            str(event.GetText())
            )

    def setTransparency(self, event=None):
        alpha = self.alpha_slider.GetValue()
        self.SetTransparent(alpha)
        self.options.Set("GuiAlpha", alpha)
        self.Layout()

    def OnClose(self, event):
        self._persistMgr.SaveAndUnregister()
        # Store check-box values in pickle container
        self.options.Set("HlBlops", self.hl_blops.IsChecked())
        self.options.Set("ShowCorp", self.show_corp.IsChecked())
        self.options.Set("ShowAlliance", self.show_alliance.IsChecked())
        self.options.Set("ShowFaction", self.show_faction.IsChecked())
        self.options.Set("HlGalMin", self.ignore_galmin.IsChecked())
        self.options.Set("HlAmaCal", self.ignore_amacal.IsChecked())
        self.options.Set("HlNone", self.ignore_none.IsChecked())
        # Delete last outlist
        self.options.Set("outlist", None)
        # Store version information
        self.options.Set("version", config.CURRENT_VER)
        # Write pickle container to disk
        self.options.Save()
        event.Skip()

    def OnQuit(self, e):
        self.Close()

    def updateAlert(self, latest_ver, cur_ver):
        '''Gets called by chk_github_update() in chkversion.py.'''
        self.ToggleWindowStyle(wx.STAY_ON_TOP)
        msgbox = wx.MessageBox(
            "PySpy " + str(latest_ver) + " is now available. You are running " +
            str(cur_ver) + ". Would you like to update now?",
            'Update Available',
            wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION | wx.STAY_ON_TOP
            )
        if msgbox == wx.YES:
            webbrowser.open_new_tab(
                "https://github.com/WhiteRusssian/PySpy/releases/latest"
                )
        self.ToggleWindowStyle(wx.STAY_ON_TOP)

    def toggleHlBlops(self, e):
        self.options.Set("HlBlops", self.hl_blops.IsChecked())
        self.updateList(self.options.Get("outlist", None))

    def toggleViewCorp(self, e):
        if self.show_corp.IsChecked():
            col_width = self.options.Get("colCorpWidth", 145)
            self.list.SetColumnWidth(self.lc_corp, col_width)
        else:
            col_width = self.list.GetColumnWidth(self.lc_corp)
            self.options.Set("colCorpWidth", col_width)
            self.list.SetColumnWidth(self.lc_corp, 0)
        self.Layout()

    def toggleViewAlliance(self, e):
        if self.show_alliance.IsChecked():
            col_width = self.options.Get("colAllianceWidth", 210)
            self.list.SetColumnWidth(self.lc_alliance, col_width)
        else:
            col_width = self.list.GetColumnWidth(self.lc_alliance)
            self.options.Set("colAllianceWidth", col_width)
            self.list.SetColumnWidth(self.lc_alliance, 0)
        self.Layout()

    def toggleViewFaction(self, e):
        if self.show_faction.IsChecked():
            col_width = self.options.Get("colFactionWidth", 90)
            self.list.SetColumnWidth(self.lc_faction, col_width)
        else:
            col_width = self.list.GetColumnWidth(self.lc_faction)
            self.options.Set("colFactionWidth", col_width)
            self.list.SetColumnWidth(self.lc_faction, 0)
        self.Layout()

    def toggleIgnoreFactions(self, e):
        ig_galmin = self.ignore_galmin.IsChecked()
        ig_amacal = self.ignore_amacal.IsChecked()
        ig_none = self.ignore_none.IsChecked()
        if ig_galmin:
            config.IGNORED_FACTIONS = 2  # Gallente & Minmatar have even ids
            self.options.Set("IgnoredFactions", 2)
        if ig_amacal:
            config.IGNORED_FACTIONS = 1  # Amarr & Caldari have uneven ids
            self.options.Set("IgnoredFactions", 1)
        if ig_none:
            config.IGNORED_FACTIONS = None  # Amarr & Caldari have uneven ids
            self.options.Set("IgnoredFactions", 0)
        self.updateList(self.options.Get("outlist", None))

    def toggleStayOnTop(self, e):
        self.options.Set("StayOnTop", self.stay_ontop.IsChecked())
        self.ToggleWindowStyle(wx.STAY_ON_TOP)


class App(wx.App):
    def OnInit(self):
        self.PySpy = Frame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.PySpy)
        self.PySpy.Show()
        return True
