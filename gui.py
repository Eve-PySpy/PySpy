# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian
# Github: <https://github.com/Eve-PySpy/PySpy>**********************
'''Simple wxpython GUI with 1 frame, using persistent properties.'''
# **********************************************************************
import datetime
import logging
import os
import webbrowser

import wx
import wx.grid as WXG
import wx.lib.agw.persist as pm

import config

import aboutdialog
import highlightdialog
import ignoredialog
import sortarray
import statusmsg
# cSpell Checker - Correct Words****************************************
# // cSpell:words wrusssian, wxpython, HRULES, VRULES, ELLIPSIZE, zkill,
# // cSpell:words blops, Unregister, russsian, chkversion, posix,
# // cSpell:words Gallente, Minmatar, Amarr, Caldari, ontop, hics, npsi
# **********************************************************************
Logger = logging.getLogger(__name__)
# Example call: Logger.info("Something badhappened", exc_info=True) ****


class Frame(wx.Frame):
    def __init__(self, *args, **kwds):

        # Persistent Options
        self.options = config.OPTIONS_OBJECT

        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE  # wx.RESIZE_BORDER
        wx.Frame.__init__(self, *args, **kwds)
        self.SetName("Main Window")

        self.Font = self.Font.Scaled(self.options.Get("FontScale", 1))

        # Set stay on-top unless user deactivated it
        if self.options.Get("StayOnTop", True):
            self.ToggleWindowStyle(wx.STAY_ON_TOP)

        # Set parameters for columns
        self.columns = (
            # Index, Heading, Format, Default Width, Can Toggle, Default Show, Menu Name, Outlist Column
            [0, "ID", wx.ALIGN_LEFT, 0, False, False, "", 0],
            [1, "Warning", wx.ALIGN_LEFT, 80, True, True, "Warning\tCTRL+ALT+X"],
            [2, "Faction ID", wx.ALIGN_LEFT, 0, False, False, "", 1],
            [3, "Character", wx.ALIGN_LEFT, 100, False, True, "", 2],
            [4, "Security", wx.ALIGN_RIGHT, 50, True, False, "&Security\tCTRL+ALT+S", 15],
            [5, "CorpID", wx.ALIGN_LEFT, 0, False, False, "", 3],
            [6, "Corporation", wx.ALIGN_LEFT, 100, True, True, "Cor&poration\tCTRL+ALT+P", 4],
            [7, "AllianceID", wx.ALIGN_LEFT, 0, False, False, "-", 5],
            [8, "Alliance", wx.ALIGN_LEFT, 150, True, True, "All&iance\tCTRL+ALT+I", 6],
            [9, "Faction", wx.ALIGN_LEFT, 50, True, False, "&Faction\tCTRL+ALT+F", 7],
            [10, "Kills", wx.ALIGN_RIGHT, 50, True, True, "&Kills\tCTRL+ALT+K", 10],
            [11, "Losses", wx.ALIGN_RIGHT, 50, True, True, "&Losses\tCTRL+ALT+L", 13],
            [12, "Last Wk", wx.ALIGN_RIGHT, 50, True, True, "Last &Wk\tCTRL+ALT+W", 9],
            [13, "Solo", wx.ALIGN_RIGHT, 50, True, False, "S&olo\tCTRL+ALT+O", 14],
            [14, "BLOPS", wx.ALIGN_RIGHT, 50, True, False, "&BLOPS\tCTRL+ALT+B", 11],
            [15, "HICs", wx.ALIGN_RIGHT, 50, True, False, "&HICs\tCTRL+ALT+H", 12],
            [16, "Last Loss", wx.ALIGN_RIGHT, 60, True, True, "Days since last Loss\tCTRL+ALT+[", 16],
            [17, "Last Kill", wx.ALIGN_RIGHT, 60, True, True, "Days since last Kill\tCTRL+ALT+]", 17],
            [18, "Avg. Attackers", wx.ALIGN_RIGHT, 100, True, True, "&Average Attackers\tCTRL+ALT+A", 18],
            [19, "Covert Cyno", wx.ALIGN_RIGHT, 100, True, True, "&Covert Cyno Probability\tCTRL+ALT+C", 19],
            [20, "Regular Cyno", wx.ALIGN_RIGHT, 100, True, True, "&Regular Cyno Probability\tCTRL+ALT+R", 20],
            [21, "Last Covert Cyno", wx.ALIGN_RIGHT, 100, True, True, "&Last Covert Cyno Ship Loss\tCTRL+ALT+<", 21],
            [22, "Last Regular Cyno", wx.ALIGN_RIGHT, 110, True, True, "&Last Regular Cyno Ship Loss\tCTRL+ALT+>", 22],
            [23, "Abyssal Losses", wx.ALIGN_RIGHT, 100, True, False, "&Abyssal Losses\tCTRL+ALT+Y", 23],
            [24, "", None, 1, False, True, ""],  # Need for _stretchLastCol()
            )

        # Define the menu bar and menu items
        self.menubar = wx.MenuBar()
        self.menubar.SetName("Menubar")
        if os.name == "nt":  # For Windows
            self.file_menu = wx.Menu()
            self.file_about = self.file_menu.Append(wx.ID_ANY, '&About\tCTRL+A')
            self.file_menu.Bind(wx.EVT_MENU, self._openAboutDialog, self.file_about)
            self.file_quit = self.file_menu.Append(wx.ID_ANY, 'Quit PySpy')
            self.file_menu.Bind(wx.EVT_MENU, self.OnQuit, self.file_quit)
            self.menubar.Append(self.file_menu, 'File')
        if os.name == "posix":  # For macOS
            self.help_menu = wx.Menu()
            self.help_about = self.help_menu.Append(wx.ID_ANY, '&About\tCTRL+A')
            self.help_menu.Bind(wx.EVT_MENU, self._openAboutDialog, self.help_about)
            self.menubar.Append(self.help_menu, 'Help')

        # View menu is platform independent
        self.view_menu = wx.Menu()

        self._createShowColMenuItems()

        self.view_menu.AppendSeparator()

        # Ignore Factions submenu for view menu
        self.factions_sub = wx.Menu()
        self.view_menu.Append(wx.ID_ANY, "Ignore Factions", self.factions_sub)

        self.ignore_galmin = self.factions_sub.AppendRadioItem(wx.ID_ANY, "Gallente / Minmatar")
        self.factions_sub.Bind(wx.EVT_MENU, self._toggleIgnoreFactions, self.ignore_galmin)
        self.ignore_galmin.Check(self.options.Get("IgnoreGalMin", False))

        self.ignore_amacal = self.factions_sub.AppendRadioItem(wx.ID_ANY, "Amarr / Caldari")
        self.factions_sub.Bind(wx.EVT_MENU, self._toggleIgnoreFactions, self.ignore_amacal)
        self.ignore_amacal.Check(self.options.Get("IgnoreAmaCal", False))

        self.ignore_none = self.factions_sub.AppendRadioItem(wx.ID_ANY, "None")
        self.factions_sub.Bind(wx.EVT_MENU, self._toggleIgnoreFactions, self.ignore_none)
        self.ignore_none.Check(self.options.Get("IgnoreNone", True))

        # Higlighting submenu for view menu
        self.hl_sub = wx.Menu()
        self.view_menu.Append(wx.ID_ANY, "Highlighting", self.hl_sub)

        self.hl_blops = self.hl_sub.AppendCheckItem(wx.ID_ANY, "&BLOPS Kills\t(red)")
        self.hl_sub.Bind(wx.EVT_MENU, self._toggleHighlighting, self.hl_blops)
        self.hl_blops.Check(self.options.Get("HlBlops", True))

        self.hl_hic = self.hl_sub.AppendCheckItem(wx.ID_ANY, "&HIC Losses\t(red)")
        self.hl_sub.Bind(wx.EVT_MENU, self._toggleHighlighting, self.hl_hic)
        self.hl_hic.Check(self.options.Get("HlHic", True))

        self.hl_cyno = self.hl_sub.AppendCheckItem(
            wx.ID_ANY,
            "Cyno Characters (>" +
            "{:.0%}".format(config.CYNO_HL_PERCENTAGE) +
            " cyno losses)\t(blue)"
            )
        self.hl_sub.Bind(wx.EVT_MENU, self._toggleHighlighting, self.hl_cyno)
        self.hl_cyno.Check(self.options.Get("HlCyno", True))

        self.hl_list = self.hl_sub.AppendCheckItem(wx.ID_ANY, "&Highlighted Entities List\t(pink)")
        self.hl_sub.Bind(wx.EVT_MENU, self._toggleHighlighting, self.hl_list)
        self.hl_list.Check(self.options.Get("HlList", True))

        # Font submenu for font scale
        self.font_sub = wx.Menu()
        self.view_menu.Append(wx.ID_ANY, "Font Scale", self.font_sub)

        self._fontScaleMenu(config.FONT_SCALE_MIN, config.FONT_SCALE_MAX)

        self.view_menu.AppendSeparator()

        # Toggle Stay on-top
        self.stay_ontop = self.view_menu.AppendCheckItem(
            wx.ID_ANY, 'Stay on-&top\tCTRL+T'
            )
        self.view_menu.Bind(wx.EVT_MENU, self._toggleStayOnTop, self.stay_ontop)
        self.stay_ontop.Check(self.options.Get("StayOnTop", True))

        # Toggle Dark-Mode
        self.dark_mode = self.view_menu.AppendCheckItem(
            wx.ID_ANY, '&Dark Mode\tCTRL+D'
            )
        self.dark_mode.Check(self.options.Get("DarkMode", False))
        self.view_menu.Bind(wx.EVT_MENU, self._toggleDarkMode, self.dark_mode)
        self.use_dm = self.dark_mode.IsChecked()

        self.menubar.Append(self.view_menu, 'View ')  # Added space to avoid autogenerated menu items on Mac

        # Options Menubar
        self.opt_menu = wx.Menu()

        self.review_ignore = self.opt_menu.Append(wx.ID_ANY, "&Review Ignored Entities\tCTRL+R")
        self.opt_menu.Bind(
            wx.EVT_MENU,
            self._openIgnoreDialog,
            self.review_ignore
            )

        self.review_highlight = self.opt_menu.Append(wx.ID_ANY, "&Review Highlighted Entities\tCTRL+H")
        self.opt_menu.Bind(
            wx.EVT_MENU,
            self._openHightlightDialog,
            self.review_highlight
        )

        self.opt_menu.AppendSeparator()

        self.ignore_all = self.opt_menu.Append(wx.ID_ANY, "&Set NPSI Ignore List\tCTRL+SHIFT+S")
        self.opt_menu.Bind(
            wx.EVT_MENU,
            self._showNpsiDialog,
            self.ignore_all
            )

        self.clear_ignore = self.opt_menu.Append(wx.ID_ANY, "&Clear NPSI Ignore List\tCTRL+SHIFT+C")
        self.opt_menu.Bind(
            wx.EVT_MENU,
            self._clearNpsiList,
            self.clear_ignore
            )

        self.opt_menu.AppendSeparator()

        # Toggle zKillboard linking mode
        self.zkill_mode = self.opt_menu.AppendCheckItem(
            wx.ID_ANY, '&zKillboard Advanced Linking\tCTRL+ALT+Z'
        )
        self.zkill_mode.Check(self.options.Get("ZkillMode", False))
        self.opt_menu.Bind(wx.EVT_MENU, self._toggleZkillMode, self.zkill_mode)
        self.use_adv_zkill = self.zkill_mode.IsChecked()

        self.menubar.Append(self.opt_menu, 'Options')

        # Set the grid object
        self.grid = wx.grid.Grid(self, wx.ID_ANY)
        self.grid.CreateGrid(0, 0)
        self.grid.SetName("Output List")

        # Allow to change window transparency using this slider.
        self.alpha_slider = wx.Slider(self, wx.ID_ANY, 250, 50, 255)
        self.alpha_slider.SetName("Transparency_Slider")
        self.Bind(wx.EVT_SLIDER, self._setTransparency)

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

        # Column resize to trigger last column stretch to fill blank canvas.
        self.Bind(wx.grid.EVT_GRID_COL_SIZE, self._stretchLastCol, self.grid)

        # Window resize to trigger last column stretch to fill blank canvas.
        self.Bind(wx.EVT_SIZE, self._stretchLastCol, self)

        # Ensure that Persistence Manager saves window location on close
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Bind double click on list item to zKill link.
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self._goToZKill, self.grid)

        # Bind right click on list item to ignore character.
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self._showContextMenu, self.grid)

        # Bind left click on column label to sorting
        self.Bind(wx.grid.EVT_GRID_COL_SORT, self.sortOutlist, self.grid)

        # Set transparency based off restored slider
        self._setTransparency()
        self.__do_layout()

    def __set_properties(self, dark_toggle=None):
        '''
        Set the initial properties for the various widgets.

        :param `dark_toggle`: Boolean indicating if only the properties
        related to the colour scheme should be set or everything.
        '''
        # Colour Scheme Dictionaries
        self.dark_dict = config.DARK_MODE
        self.normal_dict = config.NORMAL_MODE

        # Colour Scheme
        if not self.options.Get("DarkMode", False):
            self.bg_colour = self.normal_dict["BG"]
            self.txt_colour = self.normal_dict["TXT"]
            self.lne_colour = self.normal_dict["LNE"]
            self.lbl_colour = self.normal_dict["LBL"]
            self.hl1_colour = self.normal_dict["HL1"]
            self.hl2_colour = self.normal_dict["HL2"]
            self.hl3_colour = self.normal_dict["HL3"]
        else:
            self.bg_colour = self.dark_dict["BG"]
            self.txt_colour = self.dark_dict["TXT"]
            self.lne_colour = self.dark_dict["LNE"]
            self.lbl_colour = self.dark_dict["LBL"]
            self.hl1_colour = self.dark_dict["HL1"]
            self.hl2_colour = self.dark_dict["HL2"]
            self.hl3_colour = self.dark_dict["HL3"]

        # Set default colors
        self.SetBackgroundColour(self.bg_colour)
        self.SetForegroundColour(self.txt_colour)
        self.grid.SetDefaultCellBackgroundColour(self.bg_colour)
        self.grid.SetDefaultCellTextColour(self.txt_colour)
        self.grid.SetGridLineColour(self.lne_colour)
        self.grid.SetLabelBackgroundColour(self.bg_colour)
        self.grid.SetLabelTextColour(self.lbl_colour)
        self.status_label.SetForegroundColour(self.lbl_colour)

        # Do not reset window size etc. if only changing colour scheme.
        if dark_toggle:
            return

        self.SetTitle(config.GUI_TITLE)
        self.SetSize((720, 400))
        self.SetMenuBar(self.menubar)
        # Insert columns based on parameters provided in col_def

        # self.grid.CreateGrid(0, 0)
        if self.grid.GetNumberCols() < len(self.columns):
            self.grid.AppendCols(len(self.columns))
        self.grid.SetColLabelSize(self.grid.GetDefaultRowSize() + 2)
        self.grid.SetRowLabelSize(0)
        self.grid.EnableEditing(0)
        self.grid.DisableCellEditControl()
        self.grid.EnableDragRowSize(0)
        self.grid.EnableDragGridSize(0)
        self.grid.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_BOTTOM)
        self.grid.ClipHorzGridLines(False)
        # self.grid.ClipVertGridLines(False)
        # Disable visual highlighting of selected cell to look more like listctrl
        self.grid.SetCellHighlightPenWidth(0)
        colidx = 0
        for col in self.columns:
            self.grid.SetColLabelValue(
                col[0],  # Index
                col[1],  # Heading
                )
            # self.grid.SetColSize(colidx, col[3])
            colidx += 1
        # Transparency slider
        self.alpha_slider.SetMinSize((100, 20))
        # Window icon
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(config.ICON_FILE, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

    def __do_layout(self):
        '''
        Assigns the various widgets to sizers and calls a number of helper
        functions.
        '''
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_bottom = wx.BoxSizer(wx.HORIZONTAL)
        sizer_main.Add(self.grid, 1, wx.EXPAND, 0)
        sizer_bottom.Add(self.status_label, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        static_line = wx.StaticLine(self, wx.ID_ANY, style=wx.LI_VERTICAL)
        sizer_bottom.Add(static_line, 0, wx.EXPAND, 0)
        sizer_bottom.Add(self.alpha_slider, 0, wx.ALIGN_RIGHT, 0)
        sizer_main.Add(sizer_bottom, 0, wx.ALIGN_BOTTOM | wx.ALL | wx.EXPAND, 1)
        self.SetSizer(sizer_main)
        self.Layout()
        self._restoreColWidth()
        self._stretchLastCol()

    def _fontScaleMenu(self, lower, upper):
        '''
        Populates the font scale sub menu with scale percentages
        based on input bounds.

        :param `lower`: The minimum scale represented as a decimal, e.g. 0.6

        :param `upper`: The maximum scale represented as a decimal, e.g. 1.4
        '''
        for scale in range(lower, upper):
            scale = scale / 10
            self.font_sub.AppendRadioItem(wx.ID_ANY, "{:.0%}".format(scale))
            self.font_sub.Bind(
                wx.EVT_MENU,
                lambda evt, scale=scale: self._setFontScale(scale, evt),
                self.font_sub.MenuItems[-1]
                )
            if scale == self.options.Get("FontScale", 1):
                self.font_sub.MenuItems[-1].Check(True)

    def _setFontScale(self, scale, evt=None):
        '''
        Changes the font scaling and saves it in the pickle container.

        :param `scale`: Float representing the font scale.
        '''
        self.Font = self.Font.Scaled(scale)
        self.options.Set("FontScale", scale)

    def _createShowColMenuItems(self):
        '''
        Populates the View menu with show column toggle menu items for
        each column that is toggleable. It uses the information provided
        in self.columns.
        '''
        # For each column, create show / hide menu items, if hideable
        self.col_menu_items = [[] for i in self.columns]
        for col in self.columns:
            if not col[4]:  # Do not add menu item if column not hideable
                continue
            index = col[0]
            options_key = "Show" + col[1]
            menu_name = "Show " + col[6]
            self.col_menu_items[index] = self.view_menu.AppendCheckItem(
                wx.ID_ANY,
                menu_name
                )
            # Column show / hide, depending on user settings, if any
            checked = self.options.Get(
                options_key,
                self.columns[index][5]
                )
            self.col_menu_items[index].Check(
                self.options.Get(options_key, checked)
                )
            # Bind new menu item to toggleColumn method
            self.view_menu.Bind(
                wx.EVT_MENU,
                lambda evt, index=index: self._toggleColumn(index, evt),
                self.col_menu_items[index]
                )

    def _toggleColumn(self, index, event=None):
        '''
        Depending on the respective menu item state, either reveals or
        hides a column. If it hides a column, it first stores the old
        column width in self.options to allow for subsequent restore.

        :param `index`: Integer representing the index of the column
        which is to shown / hidden.
        '''
        try:
            checked = self.col_menu_items[index].IsChecked()
        except:
            checked = False
        col_name = self.columns[index][1]
        if checked:
            default_width = self.columns[index][3]
            col_width = self.options.Get(col_name, default_width)
            if col_width > 0:
                self.grid.SetColSize(index, col_width)
            else:
                self.grid.SetColSize(index, default_width)
        else:
            col_width = self.grid.GetColSize(index)
            # Only save column status if column is actually hideable
            if self.columns[index][4]:
                self.options.Set(col_name, col_width)
            self.grid.HideCol(index)
        self._stretchLastCol()

    def _stretchLastCol(self, event=None):
        '''
        Makes sure the last column fills any blank space of the
        grid. For this reason, the last list item of self.columns should
        describe an empty column.
        '''
        grid_width = self.grid.Size.GetWidth()
        cols_width = 0
        for index in range(self.columns[-1][0] + 1):
            cols_width += self.grid.GetColSize(index)
        stretch_width = grid_width - cols_width
        last_col_width = max(
            self.grid.GetColSize(index) + stretch_width,
            self.columns[index][3]
        )
        self.grid.SetColSize(index, last_col_width)
        self.Layout()
        if event is not None:
            event.Skip(True)

    def appendString(self, org, app):
        """
        Appends a String to another string with a "+" if the org string is not "".

        :param org: Original String
        :param app: String which is to be appended to the org string
        :return:
        """
        if org == "-":
            return app
        else:
            return org + " + " + app

    def updateList(self, outlist, duration=None):
        '''
        `updateList()` takes the output of `output_list()` in `analyze.py` (via
        `sortOutlist()`) or a copy thereof stored in self.option, and uses it
        to populate the grid widget. Before it does so, it checks each
        item in outlist against a list of ignored characters, corporations
        and alliances. Finally, it highlights certain characters and
        updates the statusbar message.

        :param `outlist`: A list of rows with character data.

        :param `duration`: Time in seconds taken to query all relevant
        databases for each character.
        '''
        # If updateList() gets called before outlist has been provided, do nothing
        if outlist is None:
            return
        # Clean up grid
        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(numRows=self.grid.GetNumberRows())
        self.grid.AppendRows(len(outlist))
        # Add any NPSI fleet related characters to ignored_list
        npsi_list = self.options.Get("NPSIList", default=[])
        ignored_list = self.options.Get("ignoredList", default=[])
        highlighted_list = self.options.Get("highlightedList", default=[])
        hl_blops = self.options.Get("HlBlops", True)
        hl_hic = self.options.Get("HlHic", True)
        hl_cyno = self.options.Get("HlCyno", True)
        hl_list = self.options.Get("HlList", True)
        hl_cyno_prob = config.CYNO_HL_PERCENTAGE
        ignore_count = 0
        rowidx = 0
        for r in outlist:

            ignore = False
            for rec in ignored_list:
                if r[0] == rec[0] or r[3] == rec[0] or r[5] == rec[0]:
                    ignore = True
            for rec in npsi_list:
                if r[0] == rec[0]:
                    ignore = True
            if ignore:
                self.grid.HideRow(rowidx)
                ignore_count += 1

            # Schema depending on output_list() in analyze.py
            id = r[0]  # Hidden, used for zKillboard link
            faction_id = r[1]  # Hidden, used for faction ignoring
            name = r[2]
            corp_id = r[3]
            corp_name = r[4]
            alliance_id = r[5]
            alliance_name = r[6]
            faction = r[7] if r[7] is not None else "-"
            allies = "{:,}".format(int(r[8]))

            # Add number of allies to alliance name
            if alliance_name is not None:
                alliance_name = alliance_name + " (" + allies + ")"
            else:
                alliance_name = "-"

            # zKillboard data is "n.a." unless available
            week_kills = kills = blops_kills = hic_losses = "n.a."
            losses = solo_ratio = sec_status = "n.a."

            if r[13] is not None:
                week_kills = "{:,}".format(int(r[9])) if int(r[9]) >0 else "-"
                kills = "{:,}".format(int(r[10]))
                blops_kills = "{:,}".format(int(r[11])) if int(r[11]) >0 else "-"
                hic_losses = "{:,}".format(int(r[12])) if int(r[12]) >0 else "-"
                losses = "{:,}".format(int(r[13]))
                solo_ratio = "{:.0%}".format(float(r[14]))
                sec_status = "{:.1f}".format(float(r[15]))

            # PySpy proprietary data is "n.a." unless available
            last_loss = last_kill = covert_ship = normal_ship = "n.a."
            avg_attackers = covert_prob = normal_prob = abyssal_losses = "n.a."
            cov_prob_float = norm_prob_float = 0
            if r[16] is not None:

                if int(r[16]) > 0:
                    last_loss = str((
                        datetime.date.today() -
                        datetime.datetime.strptime(str(r[16]),'%Y%m%d').date()
                        ).days) + "d"
                else:
                    last_loss = "n.a."

                if int(r[17]) > 0:
                    last_kill = str((
                        datetime.date.today() -
                        datetime.datetime.strptime(str(r[17]),'%Y%m%d').date()
                        ).days) + "d"
                else:
                    last_kill = "n.a."

                avg_attackers = "{:.1f}".format(float(r[18]))
                cov_prob_float = r[19]
                covert_prob = "{:.0%}".format(cov_prob_float) if cov_prob_float >0 else "-"
                norm_prob_float = r[20]
                normal_prob = "{:.0%}".format(norm_prob_float) if norm_prob_float >0 else "-"
                covert_ship = r[21]
                normal_ship = r[22]
                abyssal_losses = r[23] if int(r[23]) >0 else "-"

            out = [
                id,
                "-",
                faction_id,
                name,
                sec_status,
                corp_id,
                corp_name,
                alliance_id,
                alliance_name,
                faction,
                kills,
                losses,
                week_kills,
                solo_ratio,
                blops_kills,
                hic_losses,
                last_loss,
                last_kill,
                avg_attackers,
                covert_prob,
                normal_prob,
                covert_ship,
                normal_ship,
                abyssal_losses
                ]

            # Check if character belongs to a faction that should be ignored
            if faction_id != 0:
                if config.IGNORED_FACTIONS == 2 and faction_id % 2 == 0:
                    self.grid.HideRow(rowidx)
                if config.IGNORED_FACTIONS == 1 and faction_id % 2 != 0:
                    self.grid.HideRow(rowidx)
            colidx = 0

            if hl_blops and r[9] is not None and r[11] > 0:  # Add BLOPS to Warning Column
                out[1] = self.appendString(out[1], "BLOPS")
            if hl_hic and r[9] is not None and r[12] > 0:
                out[1] = self.appendString(out[1], "HIC")  # Add HIC to Warning Column
            if hl_cyno and (
                    cov_prob_float >= hl_cyno_prob or norm_prob_float >= hl_cyno_prob):  # Add CYNO to Warnin Column
                out[1] = self.appendString(out[1], "CYNO")

            # Cell text formatting
            for value in out:
                color = False
                self.grid.SetCellValue(rowidx, colidx, str(value))
                self.grid.SetCellAlignment(self.columns[colidx][2], rowidx, colidx)
                if hl_blops and r[9] is not None and r[11] > 0:  # Highlight BLOPS chars
                    self.grid.SetCellTextColour(rowidx, colidx, self.hl1_colour)
                    color = True
                if hl_hic and r[9] is not None and r[12] > 0:  # Highlight HIC chars
                    self.grid.SetCellTextColour(rowidx, colidx, self.hl1_colour)
                    color = True
                if hl_cyno and (
                        cov_prob_float >= hl_cyno_prob or norm_prob_float >= hl_cyno_prob):  # Highlight CYNO chars
                    self.grid.SetCellTextColour(rowidx, colidx, self.hl2_colour)
                    color = True

                for entry in highlighted_list:  # Highlight chars from highlight list
                    if hl_list and (entry[1] == out[3] or entry[1] == out[6]or entry[1] == out[8][:-4]):
                        self.grid.SetCellTextColour(rowidx, colidx, self.hl3_colour)
                        color = True

                if not color:
                    self.grid.SetCellTextColour(rowidx, colidx, self.txt_colour)
                colidx += 1
            rowidx += 1

        if duration is not None:
            statusmsg.push_status(
                str(len(outlist) - ignore_count) +
                " characters analysed, in " + str(duration) +
                " seconds (" + str(ignore_count) + " ignored). Double click " +
                "character to go to zKillboard."
                )
        else:
            statusmsg.push_status(
                str(len(outlist) - ignore_count) + " characters analysed (" +
                str(ignore_count) + " ignored). Double click character to go " +
                " to zKillboard."
                )

    def updateStatusbar(self, msg):
        '''Gets called by push_status() in statusmsg.py.'''
        if isinstance(msg, str):
            self.status_label.SetLabel(msg)
            self.Layout()

    def _goToZKill(self, event):
        rowidx = event.GetRow()

        url = "https://zkillboard.com/"

        # If we want zkillboard advanced linking then just link to the character sheet
        if self.options.Get("ZkillMode", False):
            colidx = event.GetCol()

            # Corporation was clicked on, link to that killboard
            if colidx == 5:
                corporation_id = self.options.Get("outlist")[rowidx][3]
                url = url + "corporation/" + str(corporation_id) + "/"

            # Alliance was clicked on, link to that killboard if alliance exists
            elif colidx == 7:
                alliance_id = self.options.Get("outlist")[rowidx][5]
                if alliance_id != None:
                    url = url + "alliance/" + str(alliance_id) + "/"

            # Faction was clicked on, link to that killboard if faction exists
            elif colidx == 8:
                faction_id = self.options.Get("outlist")[rowidx][1]
                if faction_id != None:
                    url = url + "faction/" + str(faction_id) + "/"

            # Something other than character was clicked on but we want to look at the character with modifiers
            elif colidx != 2:
                # Set up the character base url
                character_id = self.options.Get("outlist")[rowidx][0]
                url = url + "character/" + str(character_id) + "/"

                # Kills modifier
                if colidx == 9:
                    url = url + "kills/"
                # Losses modifier
                elif colidx == 10:
                    url = url + "losses/"
                # Solo Modifier
                elif colidx == 12:
                    url = url + "solo/"
                # BLOPS Modifer
                elif colidx == 13:
                    url = url + "group/898/"
                # HIC Modifier
                elif colidx == 14:
                    url = url + "group/894/"
                # Abyssal Modifier
                elif colidx:
                    url = url + "abyssal/"

            # This is a catch all if the url wasnt set or if a column other than a special one was clicked.
            # This is in a seperate flow to the above in case any of the above need to fall through
        if url == "https://zkillboard.com/":
            character_id = self.options.Get("outlist")[rowidx][0]
            url = url + "character/" + str(character_id) + "/"

        webbrowser.open_new_tab(url)

    def _showContextMenu(self, event):
        '''
        Gets invoked by right click on any list item and produces a
        context menu that allows the user to add the selected character/corp/alliance
        to PySpy's list of "ignored characters" which will no longer be
        shown in search results and add the selected character/corp/alliance
        to PySpy's list of "highlighted characters" which will hihglight them in the grid.
        '''
        def OnIgnore(id, name, type, e=None):
            ignored_list = self.options.Get("ignoredList", default=[])
            ignored_list.append([id, name, type])
            self.options.Set("ignoredList", ignored_list)
            self.updateList(self.options.Get("outlist", None))

        def OnHighlight(id, name, type, e=None):
            highlighted_list = self.options.Get("highlightedList", default=[])
            if [id, name, type] not in highlighted_list:
                highlighted_list.append([id, name, type])
            self.options.Set("highlightedList", highlighted_list)
            self.updateList(self.options.Get("outlist", None))

        def OnDeHighlight(id, name, type, e=None):
            highlighted_list = self.options.Get("highlightedList", default=[])
            highlighted_list.remove([id, name, type])
            self.options.Set("highlightedList", highlighted_list)
            self.updateList(self.options.Get("outlist", None))

        highlighted_list = self.options.Get("highlightedList", default=[])
        rowidx = event.GetRow()
        character_id = str(self.options.Get("outlist")[rowidx][0])
        # Only open context menu character item right clicked, not empty line.
        if len(character_id) > 0:
            outlist = self.options.Get("outlist")
            for r in outlist:
                if str(r[0]) == character_id:
                    character_id = r[0]
                    character_name = r[2]
                    corp_id = r[3]
                    corp_name = r[4]
                    alliance_id = r[5]
                    alliance_name = r[6]
                    break
            self.menu = wx.Menu()
            # Context menu to ignore characters, corporations and alliances.
            item_ig_char = self.menu.Append(
                wx.ID_ANY, "Ignore character '" + character_name + "'"
                )
            self.menu.Bind(
                wx.EVT_MENU,
                lambda evt, id=character_id, name=character_name: OnIgnore(id, name, "Character", evt),
                item_ig_char
                )

            item_ig_corp = self.menu.Append(
                wx.ID_ANY, "Ignore corporation: '" + corp_name + "'"
                )
            self.menu.Bind(
                wx.EVT_MENU,
                lambda evt, id=corp_id, name=corp_name: OnIgnore(id, name, "Corporation", evt),
                item_ig_corp
                )

            if alliance_name is not None:
                item_ig_alliance = self.menu.Append(
                    wx.ID_ANY, "Ignore alliance: '" + alliance_name + "'"
                    )
                self.menu.Bind(
                    wx.EVT_MENU,
                    lambda evt, id=alliance_id, name=alliance_name: OnIgnore(id, name, "Alliance", evt),
                    item_ig_alliance
                    )

            self.menu.AppendSeparator()

            hl_char = False
            hl_corp = False
            hl_alliance = False

            for entry in highlighted_list:
                if entry[1] == self.options.Get("outlist")[rowidx][2]:
                    hl_char = True
                if entry[1] == self.options.Get("outlist")[rowidx][4]:
                    hl_corp = True
                if alliance_name is not None:
                    if entry[1] == self.options.Get("outlist")[rowidx][6]:
                        hl_alliance = True

            # Context menu to highlight characters, corporations and alliances
            if not hl_char:
                item_hl_char = self.menu.Append(
                    wx.ID_ANY, "Highlight character '" + character_name + "'"
                )
                self.menu.Bind(
                   wx.EVT_MENU,
                   lambda evt, id=character_id, name=character_name: OnHighlight(id, name, "Character", evt),
                    item_hl_char
                )
            else:
                item_hl_char = self.menu.Append(
                    wx.ID_ANY, "Stop highlighting character '" + character_name + "'"
                )
                self.menu.Bind(
                    wx.EVT_MENU,
                    lambda evt, id=character_id, name=character_name: OnDeHighlight(id, name, "Character", evt),
                    item_hl_char
                )

            if not hl_corp:
                item_hl_corp = self.menu.Append(
                    wx.ID_ANY, "Highlight corporation '" + corp_name + "'"
                )
                self.menu.Bind(
                    wx.EVT_MENU,
                    lambda evt, id=corp_id, name=corp_name: OnHighlight(id, name, "Corporation", evt),
                    item_hl_corp
                )
            else:
                item_hl_corp = self.menu.Append(
                    wx.ID_ANY, "Stop highlighting corporation '" + corp_name + "'"
                )
                self.menu.Bind(
                    wx.EVT_MENU,
                    lambda evt, id=corp_id, name=corp_name: OnDeHighlight(id, name, "Corporation", evt),
                    item_hl_corp
                )

            if alliance_name is not None:
                if not hl_alliance:
                    item_hl_alliance = self.menu.Append(
                        wx.ID_ANY, "Highlight alliance: '" + alliance_name + "'"
                        )
                    self.menu.Bind(
                        wx.EVT_MENU,
                        lambda evt, id=alliance_id, name=alliance_name: OnHighlight(id, name, "Alliance", evt),
                        item_hl_alliance
                        )
                else:
                    item_hl_alliance = self.menu.Append(
                        wx.ID_ANY, "Stop highlighting alliance: '" + alliance_name + "'"
                    )
                    self.menu.Bind(
                        wx.EVT_MENU,
                        lambda evt, id=alliance_id, name=alliance_name: OnDeHighlight(id, name, "Alliance", evt),
                        item_hl_alliance
                    )

            self.PopupMenu(self.menu, event.GetPosition())
            self.menu.Destroy()

    def sortOutlist(self, event=None, outlist=None, duration=None):
        '''
        If called by event handle, i.e. user
        '''
        if event is None:
            # Default sort by character name ascending.
            colidx = self.options.Get("SortColumn", self.columns[3][7])
            sort_desc = self.options.Get("SortDesc", False)
        else:
            colidx = event.GetCol()
            if self.options.Get("SortColumn", -1) == colidx:
                sort_desc = not self.options.Get("SortDesc")
            else:
                sort_desc = True

        # Use unicode characters for sort indicators
        arrow = u"\u2193" if sort_desc else u"\u2191"

        # Reset all labels
        for col in self.columns:
            self.grid.SetColLabelValue(col[0], col[1])

        # Assign sort indicator to sort column
        self.grid.SetColLabelValue(
            colidx,
            self.columns[colidx][1] + " " + arrow
            )
        self.options.Set("SortColumn", colidx)
        self.options.Set("SortDesc", sort_desc)
        event = None
        # Sort outlist. Note: outlist columns are not the same as
        # self.grid columns!!!
        if outlist is None:
            outlist = self.options.Get("outlist", False)

        if outlist and colidx != 1:
            outlist = sortarray.sort_array(
                outlist,
                self.columns[colidx][7],
                sec_col=self.columns[2][7],  # Secondary sort by name
                prim_desc=sort_desc,
                sec_desc=False,  # Secondary sort by name always ascending
                case_sensitive=False
                )
        self.options.Set("outlist", outlist)
        self.updateList(outlist, duration=duration)

    def _setTransparency(self, event=None):
        '''
        Sets window transparency based off slider setting and stores
        value in self.options.
        '''
        alpha = self.alpha_slider.GetValue()
        self.SetTransparent(alpha)
        self.options.Set("GuiAlpha", alpha)
        self.Layout()

    def updateAlert(self, latest_ver, cur_ver):
        '''
        Simple dialog box to notify user when new version of PySpy is
        available for download. Gets called by chk_github_update()
        in chkversion.py.
        '''
        self.ToggleWindowStyle(wx.STAY_ON_TOP)
        msgbox = wx.MessageBox(
            "PySpy " + str(latest_ver) + " is now available. You are running " +
            str(cur_ver) + ". Would you like to update now?",
            'Update Available',
            wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION | wx.STAY_ON_TOP
            )
        if msgbox == wx.YES:
            webbrowser.open_new_tab(
                "https://github.com/Eve-PySpy/PySpy/releases/latest"
                )
        self.ToggleWindowStyle(wx.STAY_ON_TOP)

    def _toggleIgnoreFactions(self, e):
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

    def _toggleHighlighting(self, e):
        self.options.Set("HlBlops", self.hl_blops.IsChecked())
        self.options.Set("HlCyno", self.hl_cyno.IsChecked())
        self.options.Set("HlHic", self.hl_hic.IsChecked())
        self.options.Set("HlList", self.hl_list.IsChecked())
        self.updateList(self.options.Get("outlist", None))

    def _toggleStayOnTop(self, evt=None):
        self.options.Set("StayOnTop", self.stay_ontop.IsChecked())
        self.ToggleWindowStyle(wx.STAY_ON_TOP)

    def _toggleDarkMode(self, evt=None):
        self.options.Set("DarkMode", self.dark_mode.IsChecked())
        self.use_dm = self.dark_mode.IsChecked()
        self.__set_properties(dark_toggle=True)
        self.Refresh()
        self.Update()
        self.updateList(self.options.Get("outlist"))

    def _openAboutDialog(self, evt=None):
        '''
        Checks if AboutDialog is already open. If not, opens the dialog
        window, otherwise brings the existing dialog window to the front.
        '''
        for c in self.GetChildren():
            if c.GetName() == "AboutDialog":  # Needs to match name in aboutdialog.py
                c.Raise()
                return
        aboutdialog.showAboutBox(self)

    def _openIgnoreDialog(self, evt=None):
        '''
        Checks if IgnoreDialog is already open. If not, opens the dialog
        window, otherwise brings the existing dialog window to the front.
        '''
        for c in self.GetChildren():
            if c.GetName() == "IgnoreDialog":  # Needs to match name in ignoredialog.py
                c.Raise()
                return
        ignoredialog.showIgnoreDialog(self)

    def _openHightlightDialog(self, evt=None):
        '''
        Checks if HightlightDialog is already open. If not, opens the dialog
        window, otherwise brings the existing dialog window to the front.
        '''
        for c in self.GetChildren():
            if c.GetName() == "HighlightDialog":  # Needs to match name in highlightdialog.py
                c.Raise()
                return
        highlightdialog.showHighlightDialog(self)

    def _showNpsiDialog(self, evt=None):
        dialog = wx.MessageBox(
            "Do you want to ignore all currently shown characters? " +
            "You can undo this under `Options > Clear NPSI Ignore List`.",
            "NPSI Ignore List",
            wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION
            )
        if dialog == 2:  # Yes
            npsi_list = []
            outlist = self.options.Get("outlist", None)
            if outlist is None:
                return
            for r in outlist:
                character_id = [r[0]]  # Needs to be list to append to ignored_list
                npsi_list.append(character_id)
            self.options.Set("NPSIList", npsi_list)
            self.updateList(outlist)

    def _clearNpsiList(self, evt=None):
        dialog = wx.MessageBox(
            "Would you like to clear the current NPSI fleet ignore list?",
            "NPSI Ignore List",
            wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION
            )
        if dialog == 2:  # Yes
            self.options.Set("NPSIList", [])
            self.updateList(self.options.Get("outlist", None))

    def _toggleZkillMode(self, evt=None):
        self.options.Set("ZkillMode", self.zkill_mode.IsChecked())
        self.use_adv_zkill = self.zkill_mode.IsChecked()
        # This just prevents all settings from being updated.
        self.__set_properties(dark_toggle=True)
        self.Refresh()
        self.Update()
        self.updateList(self.options.Get("outlist"))

    def _restoreColWidth(self):
        '''
        Restores column width either to default or value stored from
        previous session.
        '''
        for col in self.columns:
            header = col[1]
            # Column width is also set in _toggleColumn()
            width = self.options.Get(header, col[3])
            menu_item = self.col_menu_items[col[0]]
            if menu_item == [] or menu_item.IsChecked():
                self.grid.SetColSize(col[0], width)
            else:
                self.grid.SetColSize(col[0], 0)
            pass

    def _saveColumns(self):
        '''
        Saves custom column widths, since wxpython's Persistence Manager
        is unable to do so for Grid widgets.
        '''
        for col in self.columns:
            is_hideable = col[4]
            default_show = col[5]
            header = col[1]
            options_key = "Show" + header
            width = self.grid.GetColSize(col[0])
            try:
                menu_item_chk = self.col_menu_items[col[0]].IsChecked()
            except:
                menu_item_chk = False
            # Only save column width for columns that are not hidden or
            # not hideable and shown by default.
            if menu_item_chk or (not is_hideable and default_show):
                self.options.Set(header, width)
            # Do not add menu item if column not hideable
            if col[4]:
                self.options.Set(options_key, menu_item_chk)
            pass

    def OnClose(self, event=None):
        '''
        Run a few clean-up tasks on close and save persistent properties.
        '''
        self._persistMgr.SaveAndUnregister()

        # Save column toggle menu state and column width in pickle container
        self._saveColumns()

        # Store check-box values in pickle container
        self.options.Set("HlBlops", self.hl_blops.IsChecked())
        self.options.Set("HlCyno", self.hl_cyno.IsChecked())
        self.options.Set("IgnoreGalMin", self.ignore_galmin.IsChecked())
        self.options.Set("IgnoreAmaCal", self.ignore_amacal.IsChecked())
        self.options.Set("IgnoreNone", self.ignore_none.IsChecked())
        self.options.Set("StayOnTop", self.stay_ontop.IsChecked())
        self.options.Set("DarkMode", self.dark_mode.IsChecked())
        # Delete last outlist and NPSIList
        self.options.Set("outlist", None)
        self.options.Set("NPSIList", [])
        # Write pickle container to disk
        self.options.Save()
        event.Skip() if event else False

    def OnQuit(self, e):
        self.Close()


class App(wx.App):
    def OnInit(self):
        self.PySpy = Frame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.PySpy)
        self.PySpy.Show()
        return True
