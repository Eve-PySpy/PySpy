# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian <wrusssian@gmail.com>***************
''' Define a few paths and constants used throughout other modules.'''
# **********************************************************************
import logging.config
import logging
import requests
import os
import sys
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

# Read current version from VERSION file
with open(resource_path('VERSION'), 'r') as ver_file:
    CURRENT_VER = ver_file.read().replace('\n', '')

# Various constants
MAX_NAMES = 500  # The max number of char names to be processed
GUI_TITLE = "PySpy v" + CURRENT_VER


# If application is frozen executable
if getattr(sys, 'frozen', False):
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
    application_path = os.path.dirname(__file__)
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
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file_handler': {
            'level': 'INFO',
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
            'level': 'INFO',
            'propagate': True
        },
    }
}
logging.config.dictConfig(LOG_DICT)
