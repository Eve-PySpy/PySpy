# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian
# Github: <https://github.com/WhiteRusssian/PySpy>**********************
''' Checks if there is a later version of PySpy available on GitHub.'''
# **********************************************************************
import logging.config
import logging
import os
import sys

import requests
import wx

import __main__
import config
# **********************************************************************
Logger = logging.getLogger(__name__)
# Example call: Logger.info("Something badhappened", exc_info=True) ****
CURRENT_VER = config.CURRENT_VER


def chk_github_update():
    # Get latest version available on GitHub
    GIT_URL = "https://raw.githubusercontent.com/WhiteRusssian/PySpy/master/VERSION"
    try:
        latest_ver = requests.get(GIT_URL).text.replace('\n', '')
        Logger.info(
            "You are running v" + CURRENT_VER + " and v" +
            latest_ver + " is the latest version available on GitHub."
            )
    except:
        Logger.info("Could not check GitHub for potential available updates.")
    if latest_ver != CURRENT_VER:
        wx.CallAfter(__main__.app.PySpy.update_alert, latest_ver, CURRENT_VER)
