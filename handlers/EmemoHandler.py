"""
Ememo Python interface
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# EmemoHandler.py
__author__ = "Lucas Campana Levy"
__email__ = 'lcampana@cablevsion.com.ar'
__version__ = (0, 1, 0)
__written_date__ = "12-10-2015:Thursday"
__title__ = "Ememmo provisioning module"

import os
import json

import requests

import utils.utils as util
from domain.models.EmemoUser import EmemoUser
from utils.logger.logger import Logger
from utils.redis import RedisClient

LOGGER = Logger(__name__)
REST_CONFIG_FILE = 'conf/rest-conf.json'
EMEMO_BASE = 'Ememo/'


class EmemoHandler:
    def __init__(self, rightnow_client):
        self.redis = RedisClient(None, None, 0)
        self.rightnow = rightnow_client

    def get_ememo_users(self):
        """
        Gets all the Ememo users
        :return: JSON with Ememo users
        """
        LOGGER.info("Getting ememo users")

        path = os.path.join(os.getcwd(), REST_CONFIG_FILE)
        if os.path.exists(path):
            with open(path, 'rt') as f:
                conf = json.load(f)
                url = conf[self.get_ememo_users.__name__]['url']
                headers = conf[self.get_ememo_users.__name__]['headers']
        else:
            LOGGER.error("Error get_ememo_users() configuration file not found")
            raise Exception("Error get_ememo_users() configuration file not found")

        if url is None:
            LOGGER.error("Error get_ememo_users() url is a required param")
            raise Exception("Error get_ememo_users() url is a required param")
        try:
            response = requests.get(url, headers=headers)
        except Exception as e:
            LOGGER.error("Error making a get_ememo_users() request: %s" % str(e))
            raise Exception(e)
        else:
            return response.json()

    @staticmethod
    def get_users_collection(ememo_users_json):
        """
        Returns a collection of EmemoUsers
        :param ememo_users_json:
        :return: EmemoUser Collection
        """
        LOGGER.info('Formatting ememo users')

        result = []
        if ememo_users_json:
            for user in ememo_users_json['idp_ememoCollection']['idp_ememo']:
                ememo_user = EmemoUser(user['user_id'], user['nombre'], user['apellido'], user['nick'],
                                       user['nombre_sector'], user['nom_udn'], user['nom_site'],
                                       user['ultimo_login'])
                result.append(ememo_user)

        return result

    def store_rightnow_users(self, rightnow_users):
        """
        Stores rightnow users internally
        :param rightnow_users:
        """
        LOGGER.info('Storing rightnow users internally')

        for rn_user in rightnow_users:
            self.redis.save(rn_user.Login, json.dumps(rn_user.__dict__))

    def get_rightnow_users(self):
        """
        Gets the rightnow users List
        :return: list of rightnow users delimited by commas
        """
        LOGGER.info('Getting rightnow users')

        query = "SELECT A.ID, A.Login, A.DisplayName FROM Account A WHERE A.Login LIKE \'" + EMEMO_BASE + "%\'"
        pagesize = 10000
        rightnow_users = self.rightnow.get_query_csv(query, pagesize)

        return rightnow_users

    def check_users(self, ememo_users):
        """
        Checks for users changes
        :param ememo_users:
        """
        LOGGER.info('Checking for ememo users create/update')

        for ememo_user in ememo_users:
            if self.redis.exists(ememo_user.base_login):
                rn_user = util.convert_dict_to_json(
                    util.convert_dict_to_utf8(self.redis.get_all(ememo_user.base_login)))
                if rn_user and rn_user['Login'] != ememo_user.base_login \
                        and rn_user['DisplayName'] != ememo_user.display_name:
                    self.rightnow.update_account(rn_user['ID'], ememo_user.base_login, ememo_user.display_name)
                elif rn_user and rn_user['Login'] != ememo_user.base_login:
                    self.rightnow.update_account(rn_user['ID'], ememo_user.base_login)
                elif rn_user['DisplayName'] != ememo_user.display_name:
                    self.rightnow.update_account(rn_user['ID'], None, ememo_user.display_name)
                self.redis.delete(ememo_user.base_login)
            else:
                self.rightnow.create_account(ememo_user.base_login, ememo_user.display_name)

    def delete_inactive_users(self):
        """
        Deletes the inactive users
        """
        LOGGER.info('Deleting inactive users')

        for key in self.redis.keys():
            key = key.decode('utf-8')
            LOGGER.info('Deleting ememo user: ' + key)
            id = util.convert_dict_to_utf8(self.redis.get_all(key))['ID']
            self.rightnow.destroy_account(id)

    def run(self):
        """
        Executes Ememo provisioning over Rightnow
        """
        LOGGER.info('Running Ememo provisioning over Rightnow')

        # flush db
        LOGGER.info('Flushing database')
        self.redis.flush_db()

        # Get all rn users
        rightnow_users = self.get_rightnow_users()

        # Store users internally
        self.store_rightnow_users(rightnow_users)

        # Get all ememo users
        ememo_users = self.get_users_collection(self.get_ememo_users())

        # Checks for users changes
        self.check_users(ememo_users)

        # Deletes inactive users
        self.delete_inactive_users()
