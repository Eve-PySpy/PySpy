# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian
# Github: <https://github.com/Eve-PySpy/PySpy>**********************
''' Provides functionality to update the status message in the
wxPython GUi.
'''
# **********************************************************************
import logging
import time

import wx

import __main__
import config
# cSpell Checker - Correct Words****************************************
# // cSpell:words russsian
# **********************************************************************
Logger = logging.getLogger(__name__)
# Example call: Logger.info("Something badhappened", exc_info=True) ****


def push_status(msg):
    wx.CallAfter(__main__.app.PySpy.updateStatusbar, msg)
