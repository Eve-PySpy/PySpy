# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian
# Github: <https://github.com/Eve-PySpy/PySpy>**********************
''' This module provides connectivity to CCP's ESI API, to zKillboard's
API and to PySpy's own proprietary RESTful API.
'''
# **********************************************************************
import json
import logging
import threading
import time

import requests

import config
import statusmsg
# cSpell Checker - Correct Words****************************************
# // cSpell:words wrusssian, ZKILL, gmail, blops, toon, HICs, russsian,
# // cSpell:words ccp's, activepvp
# **********************************************************************
Logger = logging.getLogger(__name__)
# Example call: Logger.info("Something badhappened", exc_info=True) ****


# ESI Status
# https://esi.evetech.net/ui/?version=meta#/Meta/get_status

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
            "User-Agent": "PySpy, Author: White Russsian, https://github.com/WhiteRusssian/PySpy"
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
            server_msg = "N/A"
            try:
                server_msg = json.loads(r.text)["error"]
            except:
                pass
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
            # Number of total kills
            kills = r["shipsDestroyed"]
        except (KeyError, TypeError):
            kills = 0

        try:
            # Number of BLOPS killed
            blops_kills = r["groups"]["898"]["shipsDestroyed"]
        except (KeyError, TypeError):
            blops_kills = 0

        try:
            # Number of HICs lost
            hic_losses = r["groups"]["894"]["shipsLost"]
        except (KeyError, TypeError):
            hic_losses = 0

        try:
            # Kills over past 7 days
            week_kills = r["activepvp"]["kills"]["count"]
        except (KeyError, TypeError):
            week_kills = 0

        try:
            # Number of total losses
            losses = r["shipsLost"]
        except (KeyError, TypeError):
            losses = 0

        try:
            # Ratio of solo kills to total kills
            solo_ratio = int(r["soloKills"]) / int(r["shipsDestroyed"])
        except (KeyError, TypeError):
            solo_ratio = 0

        try:
            # Security status
            sec_status = r["info"]["secStatus"]
        except (KeyError, TypeError):
            sec_status = 0

        self._queue.put(
            [kills, blops_kills, hic_losses, week_kills, losses, solo_ratio,
            sec_status, self._char_id]
            )
        return


def post_proprietary_db(character_ids):
    '''
    Query PySpy's proprietary kill database for the character ids
    provided as a list or tuple of integers. Returns a JSON containing
    one line per character id.

    :param `character_ids`: List or tuple of character ids as integers.
    :return: JSON dictionary containing certain statistics for each id.
    '''
    url = "http://pyspy.pythonanywhere.com" + "/character_intel/" + "v1/"
    headers = {
        "Accept-Encoding": "gzip",
        "User-Agent": "PySpy, Author: White Russsian, https://github.com/WhiteRusssian/PySpy"
        }
    # Character_ids is a list of tuples, which needs to be converted to dict
    # with list as value.
    character_ids = {"character_ids": character_ids}
    try:
        r = requests.post(url, headers=headers, json=character_ids)
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
            "PySpy server returned error code: " +
            str(r.status_code) + ", saying: " + server_msg, exc_info=True
            )
        statusmsg.push_status(
            "PYSPY SERVER ERROR: " + str(r.status_code) + " (" + server_msg + ")"
            )
        return "server_error"
    return r.json()


def get_ship_data():
    '''
    Produces a list of ship id and ship name pairs for each ship in EVE
    Online, using ESI's universe/names endpoint.

    :return: List of lists containing ship ids and related ship names.
    '''
    all_ship_ids = get_all_ship_ids()
    if not isinstance(all_ship_ids, (list, tuple)) or len(all_ship_ids) < 1:
        Logger.error("[get_ship_data] No valid ship ids provided.", exc_info=True)
        return

    url = "https://esi.evetech.net/v2/universe/names/?datasource=tranquility"
    json_data = json.dumps(all_ship_ids)
    try:
        r = requests.post(url, json_data)
    except requests.exceptions.ConnectionError:
        Logger.error("[get_ship_data] No network connection.", exc_info=True)
        return "network_error"
    if r.status_code != 200:
        server_msg = json.loads(r.text)["error"]
        Logger.error(
            "[get_ship_data] CCP Servers returned error code: " +
            str(r.status_code) + ", saying: " + server_msg, exc_info=True
            )
        return "server_error"
    ship_data = list(map(lambda r: [r['id'], r['name']], r.json()))
    return ship_data


def get_all_ship_ids():
    '''
    Uses ESI's insurance/prices endpoint to get all available ship ids.

    :return: List of ship ids as integers.
    '''
    url = "https://esi.evetech.net/v1/insurance/prices/?datasource=tranquility"

    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        Logger.error("[get_ship_ids] No network connection.", exc_info=True)
        return "network_error"
    if r.status_code != 200:
        server_msg = json.loads(r.text)["error"]
        Logger.error(
            "[get_ship_ids] CCP Servers at returned error code: " +
            str(r.status_code) + ", saying: " + server_msg, exc_info=True
            )
        return "server_error"

    ship_ids = list(map(lambda r: str(r['type_id']), r.json()))
    Logger.info("[get_ship_ids] Number of ship ids found: " + str(len(ship_ids)))
    return ship_ids