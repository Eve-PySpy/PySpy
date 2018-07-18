# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian
# Github: <https://github.com/WhiteRusssian/PySpy>**********************
'''Establishes an in memory SQLite3 database and creates a few tables as
well as provides a function to write records to the database.'''
# **********************************************************************
import logging
import sqlite3

import config
# cSpell Checker - Correct Words****************************************
# // cSpell:words wrusssian, sqlite, blops, russsian
# **********************************************************************
Logger = logging.getLogger(__name__)
# Example call: Logger.info("Something badhappened", exc_info=True) ****


def connect_db():
    '''Create in memory database
    @returns: connection and curser objects as conn and cur'''
    conn = sqlite3.connect(":memory:")
    conn.isolation_level = None
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode = TRUNCATE")
    prepare_tables(conn, cur)
    return conn, cur


def prepare_tables(conn, cur):
    '''Create a few tables, unless they already exist. Do not close the
    connection as it will continue to be used by the calling
    function.'''
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS characters (char_name TEXT, char_id INT,
        corp_id INT, alliance_id INT, faction_id INT, kills INT,
        blops_kills INT, hic_losses INT, week_kills INT)'''
        )
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS corporations (id INT, name TEXT)'''
        )
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS alliances (id INT, name TEXT)'''
        )
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS factions (id INT, name TEXT)'''
        )
    cur.executemany(
        '''INSERT INTO factions (id, name) VALUES (?, ?)''',
        config.FACTION_IDS
    )
    conn.commit()


def write_many_to_db(conn, cur, query_string, records, keepalive=True):
    '''Take a database connection and write records to it. Afterwards,
    leave the connection alive, unless keepalive=False and return the
    number of records added to the database.
    @returns: records_added'''
    try:
        cur.executemany(query_string, records)
        conn.commit()
    except Exception:
        Logger.error("Failed to write orders to database.", exc_info=True)
        raise Exception
    records_added = conn.total_changes
    if not keepalive:
        cur.execute("PRAGMA optimize")
        conn.close()
    return records_added
