"""
Redis client module
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# redis.py
__author__ = "Lucas Campana Levy"
__email__ = 'lcampana@cablevsion.com.ar'
__version__ = (0, 1, 0)
__written_date__ = "09-10-2015:Thursday"
__title__ = "Redis client module"

import os
import json

import redis

from utils.logger.logger import Logger

LOGGER = Logger(__name__)
REDIS_CONFIG_FILE = 'conf/redis-conf.json'


class RedisClient:
    def __init__(self, host=None, port=None, db=0):
        """
        Default Constructor
        :param host:
        :param port:
        :param db:
        :return:
        """
        LOGGER.info('Setting up Redis client')

        try:
            path = os.path.join(os.getcwd(), REDIS_CONFIG_FILE)
            if os.path.exists(path):
                with open(path, 'rt') as f:
                    config = json.load(f)
                # Connect to the database
                pool = redis.ConnectionPool(
                    host=config['host'],
                    port=config['port'],
                    db=db
                )
                self.r = redis.Redis(connection_pool=pool)
            else:
                pool = redis.ConnectionPool(
                    host=host,
                    port=port,
                    db=db
                )
                self.r = redis.Redis(connection_pool=pool)
            LOGGER.info("Redis client ready")
        except Exception as e:
            LOGGER.error("Could not connect to redis server: %s" % str(e))
            raise Exception("Could not connect to redis server: %s" % str(e))

    def save(self, key, value):
        """
        Saves record

        :param key:
        :param value:
        """

        LOGGER.debug("Saving key: [" + key + "], value: [" + value + "]")

        if key is None:
            LOGGER.error("Error save() key must not be null.")
            raise Exception("Error save() key must not be null.")
        if value is None:
            LOGGER.error("Error save() value must not be null.")
            raise Exception("Error save() value must not be null.")

        try:
            self.r.hmset(key, json.loads(value))
        except Exception as e:
            LOGGER.error("Error save() trying to setting values: %s" % str(e))
            raise Exception("Error save() trying to setting values: %s" % str(e))

    def keys(self, pattern='*'):
        """
        Gets list of keys that match with the name
        :param pattern:
        :return: list of keys
        """

        LOGGER.debug("Getting keys for pattern: " + pattern)

        try:
            result = self.r.keys(pattern)
        except Exception as e:
            LOGGER.error('Error keys() getting keys with pattern: [' + pattern + ']. %s' % str(e))
            raise Exception('Error keys() getting keys with pattern: [' + pattern + ']. %s' % str(e))
        else:
            return result

    def get_all(self, key):
        """
        Gets all attributes from a record by key

        :param key:
        :return record
        """

        LOGGER.debug("Getting values from key: [" + key + "]")

        if key is None:
            LOGGER.error("Error get_all() key must not be null.")
            raise Exception("Error get_all() key must not be null.")

        try:
            result = self.r.hgetall(key)
        except Exception as e:
            LOGGER.error("Error get_all() trying to get all attributes: %s" % str(e))
            raise Exception("Error get_all() trying to get all attributes: %s" % str(e))
        else:
            return result

    def get_attribute(self, key, attribute):
        """
        Gets an attributes from a record by key

        :param key:
        :param attribute
        :return attribute
        """

        LOGGER.debug("Getting attribute: [" + attribute + "] from key: [" + key + "]")

        if key is None:
            LOGGER.error("Error get_attribute() key must not be null.")
            raise Exception("Error get_attribute() key must not be null.")
        if attribute is None:
            LOGGER.error("Error get_attribute() attribute must not be null.")
            raise Exception("Error get_attribute() attribute must not be null.")

        try:
            result = self.r.hmget(key, attribute)
        except Exception as e:
            LOGGER.error("Error get_attribute() trying to get attribute: %s" % str(e))
            raise Exception("Error get_attribute() trying to get attribute: %s" % str(e))
        else:
            return result

    def exists(self, key):
        """
        Checks if key exists

        :param key:
        :return boolean
        """

        LOGGER.debug("Checking exists key: [" + key + "]")

        if key is None:
            LOGGER.error("Error exists() key must not be null.")
            raise Exception("Error exists() key must not be null.")
        try:
            result = self.r.exists(key)
        except Exception as e:
            LOGGER.error("Error exists() trying to check if exists: %s" % str(e))
            raise Exception("Error exists() checking if exists: %s" % str(e))
        else:
            return result

    def set_attribute(self, key, name, value):
        """
        Sets key / value to a name hash

        :param name:
        :param key:
        :param value:
        :return boolean
        """

        LOGGER.debug("Setting attribute key: [" + key + "], value: [" + value + "], name: [" + name + "]")

        if key is None:
            LOGGER.error("Error set_attribute() key must not be null.")
            raise Exception("Error set_attribute() key must not be null.")
        if value is None:
            LOGGER.error("Error set_attribute() value must not be null.")
            raise Exception("Error set_attribute() value must not be null.")
        if name is None:
            LOGGER.error("Error set_attribute() name must not be null.")
            raise Exception("Error set_attribute() name must not be null.")

        try:
            self.r.hset(key, name, value)
        except Exception as e:
            LOGGER.error("Error set_attribute(): %s" % str(e))
            raise Exception("Error set_attribute(): %s" % str(e))

    def pop(self, name):
        """
        Gets record by name and pops from de db
        :param name:
        :return record if exist or none if not
        """

        LOGGER.debug("Pops key: " + name)

        try:
            result = self.r.lpop(name)
        except Exception as e:
            LOGGER.error("Error pop(): %s" % str(e))
            raise Exception("Error pop(): %s" % str(e))
        else:
            return result

    def delete(self, name):
        """
        Deletes record by name
        :param name:
        """

        LOGGER.debug("Deleting key: " + name)

        try:
            self.r.delete(name)
        except Exception as e:
            LOGGER.error("Error delete() deleting " + name + ": %s" % str(e))
            raise Exception("Error delete() deleting " + name + ": %s" % str(e))

    def flush_db(self):
        """
        Flush the current database
        """

        LOGGER.debug("Flushing database")

        try:
            self.r.flushdb()
        except Exception as e:
            LOGGER.error("Error flush_db() flushing database: %s" % str(e))
            raise Exception("Error flush_db() flushing database: %s" % str(e))
