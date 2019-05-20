"""
Logging setup module
"""
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# logger.py

__author__ = "Lucas Campana Levy"
__email__ = 'lcampana@cablevsion.com.ar'
__version__ = (0, 1, 0)
__written_date__ = "12-10-2015:Thursday"
__title__ = "Logging setup module"

import os
import json
import logging
import logging.config

LOGGER_CONFIG_FILE = 'conf/logger-conf.json'


class Singleton(object):
    """
    Singleton interface:
    http://www.python.org/download/releases/2.2.3/descrintro/#__new__
    """

    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.__init__(*args, **kwds)
        return it

    def __init__(self, *args, **kwds):
        pass


class LoggerManager(Singleton):
    """
    Logger Manager.
    Handles all logging files.
    """

    def __init__(self, loggername, *args, **kwds):
        super().__init__(*args, **kwds)
        self.logger = logging.getLogger(loggername)
        path = os.path.join(os.getcwd(), LOGGER_CONFIG_FILE)
        if os.path.exists(path):
            with open(path, 'rt') as f:
                conf = json.load(f)
            logging.config.dictConfig(conf)
        else:
            logging.basicConfig(level=logging.INFO)

    def debug(self, loggername, msg):
        self.logger = logging.getLogger(loggername)
        self.logger.debug(msg)

    def error(self, loggername, msg):
        self.logger = logging.getLogger(loggername)
        self.logger.error(msg)

    def info(self, loggername, msg):
        self.logger = logging.getLogger(loggername)
        self.logger.info(msg)

    def warning(self, loggername, msg):
        self.logger = logging.getLogger(loggername)
        self.logger.warning(msg)


class Logger(object):
    """
    Logger object.
    """

    def __init__(self, loggername="root"):
        self.lm = LoggerManager(loggername)  # LoggerManager instance
        self.loggername = loggername  # logger name

    def debug(self, msg):
        self.lm.debug(self.loggername, msg)

    def error(self, msg):
        self.lm.error(self.loggername, msg)

    def info(self, msg):
        self.lm.info(self.loggername, msg)

    def warning(self, msg):
        self.lm.warning(self.loggername, msg)
