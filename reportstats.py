# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian
# Github: <https://github.com/WhiteRusssian/PySpy>**********************
''' Provides functionality to report basic usage statistics to a
webserver.
'''
# **********************************************************************
import json
import logging
import platform
import threading
import time

import requests

import config
import statusmsg
# cSpell Checker - Correct Words****************************************
# // cSpell:words russsian, blops
# **********************************************************************
Logger = logging.getLogger(__name__)
# Example call: Logger.info("Something badhappened", exc_info=True) ****


class ReportStats(threading.Thread):
    '''
    Collects a number of properties and selected user options
    and uploads those each time the user performs a character analysis,
    together with the number of characters searched and the search duration.
    Instances of ReportStats run in their own separate thread and do not
    return any values, regardless of successful upload or failure.
    '''
    # Report stats in separate thread. Do not complain if error encountered.
    def __init__(self, outlist, duration):
        super(ReportStats, self).__init__()
        self.daemon = True
        self._uuid = config.OPTIONS_OBJECT.Get("uuid")
        self._version = config.CURRENT_VER
        self._platform = platform.system()
        self._chars = str(len(outlist))
        self._duration = str(duration)
        self._sh_faction = str(config.OPTIONS_OBJECT.Get("ShowFaction", True))
        self._hl_blops = str(config.OPTIONS_OBJECT.Get("HlBlops", True))
        self._ig_factions = str(not config.OPTIONS_OBJECT.Get("HlNone", True))
        self._gui_alpha = config.OPTIONS_OBJECT.Get("GuiAlpha", 250)

    def run(self):
        url = "http://pyspy.pythonanywhere.com/add_record/"
        headers = {
            "Accept-Encoding": "gzip",
            "User-Agent": "PySpy, Author: White Russsian, https://github.com/WhiteRusssian/PySpy"
            }
        payload = {
            "uuid": self._uuid,
            "version": self._version,
            "platform": self._platform,
            "chars": self._chars,
            "duration": self._duration,
            "sh_faction": self._sh_faction,
            "hl_blops": self._hl_blops,
            "ig_factions": self._ig_factions,
            "gui_alpha": self._gui_alpha
            }

        try:
            r = requests.get(url, headers=headers, params=payload)
        except requests.exceptions.ConnectionError:
            Logger.info("No network connection.", exc_info=True)
            statusmsg.push_status(
                '''NETWORK ERROR: Check your internet connection
                and firewall settings.'''
                )
            time.sleep(5)
            return

        if r.status_code != 200:
            status_code = r.status_code
            reason = r.reason
            Logger.info(
                "Could not upload usage statistics. Server message: '" +
                reason + "'. Code: " + str(status_code) + " [URL: " + r.url + "]",
                exc_info=True
                )
        return
