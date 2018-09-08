# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian
# Github: <https://github.com/WhiteRusssian/PySpy>**********************
'''The About Dialog for PySpy's GUI. OnAboutBox() gets called by the GUI
module.'''
# **********************************************************************
import logging
import time

import wx
import wx.adv

import __main__
import config
# cSpell Checker - Correct Words****************************************
# // cSpell:words russsian, wxpython, ccp's
# // cSpell:words
# **********************************************************************
Logger = logging.getLogger(__name__)
# Example call: Logger.info("Something badhappened", exc_info=True) ****


def showAboutBox(parent, event=None):
    # __main__.app.PySpy.ToggleWindowStyle(wx.STAY_ON_TOP)

    description = """
    PySpy is an EVE Online character intel tool
    using CCP's ESI API and a daily updated proprietary
    database containing key statistics on approximately
    2.4 million pilots.

    If you enjoy PySpy and want to show your appreciation
    to its author, you are welcome to send an ISK donation
    in-game to White Russsian (with 3 "s").

    Thank you."""

    try:
        with open(config.resource_path('LICENSE.txt'), 'r') as lic_file:
            license = lic_file.read()
    except:
        license = "PySpy is licensed under the MIT License."

    info = wx.adv.AboutDialogInfo()

    info.SetIcon(wx.Icon(config.ABOUT_ICON, wx.BITMAP_TYPE_PNG))
    info.SetName("PySpy")
    info.SetVersion(config.CURRENT_VER)
    info.SetDescription(description)
    info.SetCopyright('(C) 2018 White Russsian')
    info.SetWebSite('https://github.com/WhiteRusssian/PySpy')
    info.SetLicence(license)

    wx.adv.AboutBox(info)
