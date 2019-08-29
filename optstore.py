# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian
# Github: <https://github.com/Eve-PySpy/PySpy>**********************
'''
PresistentOptions can be used to create an object that stores values
in a dictionary and save them in a pickle file for use in subsequent
sessions.
'''
# **********************************************************************
import logging
import os
import pickle

import config
# cSpell Checker - Correct Words****************************************
# // cSpell:words russsian
# **********************************************************************
Logger = logging.getLogger(__name__)
# Example call: Logger.info("Something badhappened", exc_info=True) ****


class PersistentOptions():
    '''
    :class:`PersistentOptions`: Store variables between sessions.

    Creates a dictionary object to store various variables in a
    pickle file between sessions.
    '''
    def __init__(self, options_file):
        '''
        :param `options_file`: the relative or absolute path to the pickle file;
        '''
        self._pickle_file = options_file
        self._options = self._restore()

    def ListKeys(self):
        '''
        Returns list of all keys available in class object.
        '''
        keys = []
        for key in self._options:
            keys.append(key)
        return keys

    def Get(self, key, default=None):
        '''
        Returns the value of the specified key in the dictionary object.

        :param `key`: a valid key of the dictionary object;
        :param `default`: the value that should be returned if key is invalid;
        '''
        try:
            return self._options[key]
        except KeyError:
            if default is not None:
                return default
            else:
                raise Exception("ERROR: no such key: " + str(key))

    def Set(self, key, value):
        '''
        Stores value under the specified key in the dictionary object.

        :param `key`: a new or existing key of the dictionary object;
        :param `value`: any python object;
        '''
        self._options[key] = value

    def Del(self, key):
        '''
        Deletes specified key in the dictionary object.

        :param `key`: existing key of the dictionary object;
        '''
        try:
            del self._options[key]
        except:
            raise Exception("ERROR: no such key: " + str(key))

    def Save(self):
        '''
        Saves the dictionary object in a pickle file under the file name
        provided at instantiation.
        '''
        self._storePickle(self._pickle_file, self._options)
        return

    def _restore(self):
        '''
        Restores the dictionary object from the pickle file saved under
        the file name provided at instantiation.
        '''
        return self._getPickle(self._pickle_file)

    def _storePickle(self, pickle_file, data):
        '''
        Save binary pickle to disk.

        :param `pickle_file`: absolute or relative path to pickle file;
        :param `data`: any python object;
        '''
        try:
            pickle_dir = os.path.dirname(pickle_file)
        except:
            pickle_dir = "./"
        pickle_data = data
        try:
            if not os.path.exists(pickle_dir):
                os.makedirs(pickle_dir)
            with open(pickle_file, 'wb') as file:
                pickle.dump(pickle_data, file, pickle.HIGHEST_PROTOCOL)
        except Exception:
            Logger.warn("Failed to create / store pickle file.", exc_info=True)
        finally:
            return

    def _getPickle(self, pickle_file):
        '''
        Returns data contained in pickle file or if pickle_file is not a
        valid pickle, return empty dictionary.

        :param `pickle_file`: absolute or relative path to pickle file;
        '''
        pickle_data = {}
        try:
            with open(pickle_file, 'rb') as file:
                pickle_data = pickle.load(file)
            return pickle_data
        except FileNotFoundError:
            Logger.warn("Could not find pickle file.", exc_info=True)
        finally:
            return pickle_data
