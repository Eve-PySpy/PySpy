# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian
# Github: <https://github.com/WhiteRusssian/PySpy>**********************
''' The primary function is main(), which takes a set of EVE Online
character names and gathers useful information from CCP's ESI API and
zKIllboard's API, to be stored in a temporary in-memory SQLite3 database.
'''
# **********************************************************************
import logging
import json
import threading
import queue
import time

import apis
import config
import db
import statusmsg
# cSpell Checker - Correct Words****************************************
# // cSpell:words affil, zkill, blops, qsize, numid, russsian, ccp's
# **********************************************************************
Logger = logging.getLogger(__name__)
# Example call: Logger.info("Something badhappened", exc_info=True) ****


def main(char_names):
    conn, cur = db.connect_db()
    chars_found = get_char_ids(conn, cur, char_names)
    if chars_found > 0:
        char_ids = cur.execute(
            "SELECT char_id FROM characters ORDER BY char_name"
            ).fetchall()
        q_main = queue.Queue()
        t = zKillStats(char_ids, q_main)
        t.start()
        get_char_affiliations(conn, cur)
        get_affil_names(conn, cur)
        t.join()
        zkill_stats = q_main.get()
        query_string = (
            '''UPDATE characters SET kills=?, blops_kills=?, hic_losses=?
            WHERE char_id=?'''
            )
        db.write_many_to_db(conn, cur, query_string, zkill_stats)
        output = output_list(cur)
        conn.close()
        return output
    else:
        return


def get_char_ids(conn, cur, char_names):
    char_names = json.dumps(char_names[0:config.MAX_NAMES])  # apis max char is 1000
    statusmsg.push_status("Resolving character names to IDs...")
    try:
        characters = apis.post_req_ccp("universe/ids/", char_names)
        characters = characters['characters']
    except:
        return 0
    records = ()
    for r in characters:
        records = records + ((r["id"], r["name"]),)
    query_string = (
        '''INSERT INTO characters (char_id, char_name) VALUES (?, ?)'''
        )
    records_added = db.write_many_to_db(conn, cur, query_string, records)
    return records_added


def get_char_affiliations(conn, cur):
    char_ids = cur.execute("SELECT char_id FROM characters").fetchall()
    char_ids = json.dumps(tuple([r[0] for r in char_ids]))
    statusmsg.push_status("Retrieving character affiliation IDs...")
    try:
        affiliations = apis.post_req_ccp("characters/affiliation/", char_ids)
    except:
        Logger.info("Failed to obtain character affiliations.", exc_info=True)
        raise Exception
    records = ()
    for r in affiliations:
        if "alliance_id" in r:
            records = records + (
                (r["corporation_id"], r["alliance_id"], r["character_id"]),
                )
        else:
            records = records + ((r["corporation_id"], 0, r["character_id"]),)
    query_string = (
        '''UPDATE characters SET corp_id=?, alliance_id=? WHERE char_id=?'''
        )
    records_added = db.write_many_to_db(conn, cur, query_string, records)


def get_affil_names(conn, cur):
    # use select distinct to get corp and alliance ids and reslove them
    alliance_ids = cur.execute(
        '''SELECT DISTINCT alliance_id FROM characters
        WHERE alliance_id IS NOT 0'''
        ).fetchall()
    corp_ids = cur.execute(
        "SELECT DISTINCT corp_id FROM characters WHERE corp_id IS NOT 0"
        ).fetchall()

    ids = alliance_ids + corp_ids
    ids = json.dumps(tuple([r[0] for r in ids]))

    statusmsg.push_status("Obtaining corporation and alliance names and zKillboard data...")
    try:
        names = apis.post_req_ccp("universe/names/", ids)
    except:
        Logger.info("Failed request corporation and alliance names.",
                    exc_info=True)
        raise Exception

    alliances, corporations = (), ()
    for r in names:
        if r["category"] == "alliance":
            alliances = alliances + ((r["id"], r["name"]),)
        elif r["category"] == "corporation":
            corporations = corporations + ((r["id"], r["name"]),)
    if alliances:
        query_string = ('''INSERT INTO alliances (id, name) VALUES (?, ?)''')
        db.write_many_to_db(conn, cur, query_string, alliances)
    if corporations:
        query_string = ('''INSERT INTO corporations (id, name) VALUES (?, ?)''')
        db.write_many_to_db(conn, cur, query_string, corporations)


class zKillStats(threading.Thread):

    def __init__(self, char_ids, q_main):
        super(zKillStats, self).__init__()
        self.daemon = True
        self._char_ids = char_ids
        self._q_main = q_main

    def run(self):
        count = 0
        max = 20
        threads = []
        q_sub = queue.Queue()
        for id in self._char_ids:
            t = apis.Query_zKill(id[0], q_sub)
            threads.append(t)
            t.start()
            count += 1
            time.sleep(0.05)
            if count >= max:
                break
        for t in threads:
            t.join(5)
        zkill_stats = []
        while q_sub.qsize():
            # Run through each queue item and prepare response list.
            s = q_sub.get()
            kills = str(s[0])
            blops_kills = str(s[1])
            hic_losses = str(s[2])
            id = str(s[3])
            zkill_stats.append([kills, blops_kills, hic_losses, id])
        self._q_main.put(zkill_stats)
        return


def output_list(cur):
    query_string = (
        '''SELECT
        ch.char_id, ch.char_name, co.name, al.name, ac.numid, ch.kills,
        ch.blops_kills, hic_losses
        FROM characters AS ch
        LEFT JOIN alliances AS al ON ch.alliance_id = al.id
        LEFT JOIN corporations AS co ON ch.corp_id = co.id
        LEFT JOIN (SELECT alliance_id, COUNT(alliance_id) AS numid FROM characters GROUP BY alliance_id) AS ac ON
        ch.alliance_id = ac.alliance_id
        ORDER BY ch.char_name'''
        )
    return cur.execute(query_string).fetchall()
