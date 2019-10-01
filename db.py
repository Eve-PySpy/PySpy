# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian
# Github: <https://github.com/Eve-PySpy/PySpy>**********************
'''Establishes an in memory SQLite3 database and creates a few tables as
well as provides a function to write records to the database.'''
# **********************************************************************
import datetime
import logging
import sqlite3

import config
import apis
# cSpell Checker - Correct Words****************************************
# // cSpell:words wrusssian, sqlite, blops, russsian
# **********************************************************************
Logger = logging.getLogger(__name__)
# Example call: Logger.info("Something badhappened", exc_info=True) ****


def connect_db():
    '''
    Create in memory database

    @returns: connection and cursor objects as conn and cur
    '''
    conn = sqlite3.connect(":memory:")
    conn.isolation_level = None
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode = TRUNCATE")
    prepare_tables(conn, cur)
    prepare_ship_data(conn, cur)
    return conn, cur


def prepare_tables(conn, cur):
    '''
    Create a few tables, unless they already exist. Do not close the
    connection as it will continue to be used by the calling
    function.
    '''
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS characters (char_name TEXT UNIQUE , char_id INT PRIMARY KEY ,
        corp_id INT, alliance_id INT, faction_id INT, kills INT,
        blops_kills INT, hic_losses INT, week_kills INT, losses INT,
        solo_ratio NUMERIC, sec_status NUMERIC, last_loss_date INT,
        last_kill_date INT, avg_attackers NUMERIC, covert_prob NUMERIC,
        normal_prob NUMERIC, last_cov_ship INT, last_norm_ship INT,
        abyssal_losses INT, last_update TEXT)'''
        )
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS corporations (id INT PRIMARY KEY, name TEXT)'''
        )
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS alliances (id INT PRIMARY KEY, name TEXT)'''
        )
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS factions (id INT PRIMARY KEY, name TEXT)'''
        )
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS ships (id INT PRIMARY KEY, name TEXT)'''
        )
    # Populate this table with the 4 faction warfare factions
    cur.executemany(
        '''INSERT OR REPLACE INTO factions (id, name) VALUES (?, ?)''',
        config.FACTION_IDS
        )
    conn.commit()


def prepare_ship_data(conn, cur):
    '''
    Download all ship ids and names from ESI and save in OPTIONS_OBJECT.
    '''
    ship_data_date = config.OPTIONS_OBJECT.Get("ship_data_date", 0)
    max_age = config.MAX_SHIP_DATA_AGE
    max_date = datetime.date.today() - datetime.timedelta(days=max_age)
    if ship_data_date == 0 or ship_data_date < max_date:
        config.OPTIONS_OBJECT.Set("ship_data", apis.get_ship_data())
        config.OPTIONS_OBJECT.Set("ship_data_date", datetime.date.today())
    # Populate ships table with ids and names for all ships in game
    cur.executemany(
        '''INSERT OR REPLACE INTO ships (id, name) VALUES (?, ?)''',
        config.OPTIONS_OBJECT.Get("ship_data", 0)
        )
    conn.commit()


def write_many_to_db(conn, cur, query_string, records, keepalive=True):
    '''
    Take a database connection and write records to it. Afterwards,
    leave the connection alive, unless keepalive=False and return the
    number of records added to the database.

    @returns: records_added
    '''
    try:
        cur.executemany(query_string, records)
        conn.commit()
    except Exception as e:
        Logger.error("Failed to write orders to database. {}".format(e), exc_info=True)
        raise Exception
    records_added = conn.total_changes
    if not keepalive:
        cur.execute("PRAGMA optimize")
        conn.close()
    return records_added
