# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian
# Github: <https://github.com/Eve-PySpy/PySpy>**********************
''' Define a few paths and constants used throughout other modules.'''
# **********************************************************************
import logging.config
import logging
import os
import platform
import sys
import uuid

import requests
import wx  # required for colour codes in DARK_MODE

import optstore
# cSpell Checker - Correct Words****************************************
# // cSpell:words MEIPASS, datefmt, russsian, pyinstaller, posix, pyspy
# // cSpell:words zkill, amarr, caldari, gallente, minmatar, isfile
# **********************************************************************
Logger = logging.getLogger(__name__)
# Example call: Logger.info("Something badhappened", exc_info=True) ****


# Location of packaged resource files when running pyinstaller --onefile
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)

    return os.path.join(base_path, relative_path)


# If application is frozen executable
if getattr(sys, 'frozen', False):
    ABOUT_ICON = resource_path("pyspy_mid.png")
    application_path = os.path.dirname(sys.executable)
    if os.name == "posix":
        PREF_PATH = os.path.expanduser("~/Library/Preferences")
        LOG_PATH = os.path.expanduser("~/Library/Logs")
        ICON_FILE = resource_path("pyspy.png")

    elif os.name == "nt":
        local_path = os.path.join(os.path.expandvars("%LocalAppData%"), "PySpy")
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        PREF_PATH = local_path
        LOG_PATH = local_path
        ICON_FILE = resource_path("pyspy.ico")
# If application is run as script
elif __file__:
    ABOUT_ICON = resource_path("assets/pyspy_mid.png")
    application_path = os.path.dirname(__file__)
    if platform.system() == "Linux":
        PREF_PATH = os.path.expanduser("~/.config/pyspy")
    else:
        PREF_PATH = os.path.join(application_path, "tmp")
    if not os.path.exists(PREF_PATH):
        os.makedirs(PREF_PATH)
    LOG_PATH = PREF_PATH
    if os.name == "posix":
        ICON_FILE = resource_path("assets/pyspy.png")
    elif os.name == "nt":
        ICON_FILE = resource_path("assets/pyspy.ico")

LOG_FILE = os.path.join(LOG_PATH, "pyspy.log")
GUI_CFG_FILE = os.path.join(PREF_PATH, "pyspy.cfg")
OPTIONS_FILE = os.path.join(PREF_PATH, "pyspy.pickle")
DB_FILE = os.path.join(PREF_PATH, "pyspy.sqlite3")

# Persisten options object
OPTIONS_OBJECT = optstore.PersistentOptions(OPTIONS_FILE)

# Read current version from VERSION file
with open(resource_path('VERSION'), 'r') as ver_file:
    CURRENT_VER = ver_file.read().replace('\n', '')

# Clean up old GUI_CFG_FILES and OPTIONS_OBJECT keys
if os.path.isfile(GUI_CFG_FILE) and not os.path.isfile(OPTIONS_FILE):
    try:
        os.remove(GUI_CFG_FILE)
    except:
        pass
if OPTIONS_OBJECT.Get("version", 0) != CURRENT_VER:
    print("Config file erased.")
    try:
        os.remove(GUI_CFG_FILE)
    except:
        pass
    for key in OPTIONS_OBJECT.ListKeys():
        if key != "uuid":
            OPTIONS_OBJECT.Del(key)

# Unique identifier for usage statistics reporting
if OPTIONS_OBJECT.Get("uuid", "not set") == "not set":
    OPTIONS_OBJECT.Set("uuid", str(uuid.uuid4()))

# Store version information
OPTIONS_OBJECT.Set("version", CURRENT_VER)

# Various constants
MAX_NAMES = 500  # The max number of char names to be processed
ZKILL_DELAY = 1  # API rate limit is 10/second, pushing it a little...
ZKILL_CALLS = 100
GUI_TITLE = "PySpy " + CURRENT_VER
FONT_SCALE_MIN = 7  # 7 equates to 70%
FONT_SCALE_MAX = 13
MAX_SHIP_DATA_AGE = 7  # The maximum age of ship data (used in db.prepare_ship_data)
CYNO_HL_PERCENTAGE = 0.05  # The minimum cover / normal cyno probability for highlighting
CACHE_TIME = 43200  # Seconds for which zkill requests are cached

# Colour Scheme

DARK_MODE = {
    "BG": wx.Colour(0, 0, 0),
    "TXT": wx.Colour(247, 160, 55),  # Yellow
    "LNE": wx.Colour(15, 15, 15),
    "LBL": wx.Colour(160, 160, 160),
    "HL1": wx.Colour(237, 72, 59),  # Red
    "HL2": wx.Colour(62, 157, 250),  # Blue
    "HL3": wx.Colour(237, 47, 218)  # Pink
    }

NORMAL_MODE = {
    "BG": wx.Colour(-1, -1, -1),
    "TXT": wx.Colour(45, 45, 45),
    "LNE": wx.Colour(240, 240, 240),
    "LBL": wx.Colour(32, 32, 32),
    "HL1": wx.Colour(187, 55, 46),
    "HL2": wx.Colour(38, 104, 166),
    "HL3": wx.Colour(237, 47, 218)
    }

# Note, Amarr and Caldari are allied and have IDs ending on uneven integers.
# Likewise, Gallente and Minmatar, also allied, have even IDs.
# We will use this to block certain faction alliances.
FACTION_IDS = (
    (("500001", "Caldari"), ) +
    (("500002", "Minmatar"), ) +
    (("500003", "Amarr"), ) +
    (("500004", "Gallente"), )
)
IGNORED_FACTIONS = OPTIONS_OBJECT.Get("IgnoredFactions", 0)

# Logging setup
''' For each module that requires logging, make sure to import modules
logging and this config. Then get a new logger at the beginning
of the module like this: "Logger = logging.getLogger(__name__)" and
produce log messages like this: "Logger.error("text", exc_info=True)"
'''
LOG_DETAIL = 'DEBUG'

LOG_DICT = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] (%(name)s): %(message)s',
            'datefmt': '%d-%b-%Y %I:%M:%S %p'
        },
    },
    'handlers': {
        'stream_handler': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file_handler': {
            'level': 'DEBUG',
            'filename': LOG_FILE,
            'class': 'logging.FileHandler',
            'formatter': 'standard'
        },
        'timed_rotating_file_handler': {
            'level': 'DEBUG',
            'filename': LOG_FILE,
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'D',
            'interval': 7,  # Log file rolling over every week
            'backupCount': 1,
            'formatter': 'standard'
        },
    },
    'loggers': {
        '': {
            'handlers': ['timed_rotating_file_handler', 'stream_handler'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}
logging.config.dictConfig(LOG_DICT)
