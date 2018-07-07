# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian <wrusssian@gmail.com>***************
''' This module provides connectivity to CCP's ESI API and to zKillboard's
API.
'''
# **********************************************************************
import json
import logging
import threading
import time

import requests

import config
import statusmsg
# **********************************************************************
Logger = logging.getLogger(__name__)
# Example call: Logger.info("Something badhappened", exc_info=True) ****


def post_req_ccp(esi_path, json_data):
    url = "https://esi.evetech.net/latest/" + esi_path + \
        "?datasource=tranquility"
    try:
        r = requests.post(url, json_data)
    except requests.exceptions.ConnectionError:
        Logger.info("No network connection.", exc_info=True)
        statusmsg.push_status(
            "NETWORK ERROR: Check your internet connection and firewall settings."
            )
        time.sleep(5)
        return "network_error"
    if r.status_code != 200:
        server_msg = json.loads(r.text)["error"]
        Logger.info(
            "CCP Servers at (" + esi_path + ") returned error code: " +
            str(r.status_code) + ", saying: " + server_msg, exc_info=True
            )
        statusmsg.push_status(
            "CCP SERVER ERROR: " + str(r.status_code) + " (" + server_msg + ")"
            )
        return "server_error"
    return r.json()


class Query_zKill(threading.Thread):
    # Run in a separate thread to query certain kill board statistics
    # from zKillboard's API and return the values via a queue object.
    def __init__(self, char_id, q):
        super(Query_zKill, self).__init__()
        self.daemon = True
        self._char_id = char_id
        self._queue = q

    def run(self):
        url = (
            "https://zkillboard.com/api/stats/characterID/" +
            str(self._char_id) + "/"
            )
        headers = {
            "Accept-Encoding": "gzip",
            "User-Agent": "PySpy, Author: White Russsian, wrusssian@gmail.com"
            }
        try:
            r = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            Logger.info("No network connection.", exc_info=True)
            statusmsg.push_status(
                '''NETWORK ERROR: Check your internet connection
                and firewall settings.'''
                )
            time.sleep(5)
            return "network error"
        if r.status_code != 200:
            server_msg = json.loads(r.text)["error"]
            Logger.info(
                "zKillboard server returned error for character ID " +
                str(self._char_id) + ". Error code: " + str(r.status_code),
                exc_info=True
                )
            statusmsg.push_status(
                "ZKILL SERVER ERROR: " + str(r.status_code) + " (" + server_msg + ")"
            )
            return "server error"
        try:
            r = r.json()
        except AttributeError:
            kills = 0
            blops_kills = 0
            hic_losses = 0
            self._queue.put([kills, blops_kills, self._char_id])
            return
        try:
            # Number of total kills of this toon.
            kills = r["shipsDestroyed"]
        except KeyError:
            kills = 0

        try:
            # Number of BLOPS killed by this toon.
            blops_kills = r["groups"]["898"]["shipsDestroyed"]
        except KeyError:
            blops_kills = 0

        try:
            # Number of HICs lost by this toon.
            hic_losses = r["groups"]["894"]["shipsLost"]
        except KeyError:
            hic_losses = 0

        self._queue.put([kills, blops_kills, hic_losses, self._char_id])
        return
