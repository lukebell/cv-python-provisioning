"""
Python interface interacting with a Right Now  application delivery
controller, utilizing the SOAP API to execute commands.
Work on getting the API working with python-suds.
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# soap.py
__author__ = "Lucas Campana Levy"
__email__ = 'lcampana@cablevsion.com.ar'
__version__ = (0, 1, 0)
__written_date__ = "12-10-2015:Thursday"
__title__ = "RightNow SOAP client module"

import os
import json

from suds.client import WebFault

from domain.models.RightNowAccount import RightNowAccount
from utils.soap import SOAPClient
from utils.logger.logger import Logger

LOGGER = Logger(__name__)
SOAP_CONFIG_FILE = 'conf/soap-conf.json'


class RightNowSOAP(SOAPClient):
    def __init__(self):
        """
        Default constructor
        """

        LOGGER.info("Setting up RightNow SOAP client")

        path = os.path.join(os.getcwd(), SOAP_CONFIG_FILE)
        if os.path.exists(path):
            with open(path, 'rt') as f:
                conf = json.load(f)
                self.host = conf[RightNowSOAP.__name__]['host']
                self.soap_url = conf[RightNowSOAP.__name__]['soap_url']
                self.wsdl_url = conf[RightNowSOAP.__name__]['wsdl_url']
                self.wsdl = conf[RightNowSOAP.__name__]['wsdl']
                self.username = conf[RightNowSOAP.__name__]['username']
                self.password = conf[RightNowSOAP.__name__]['password']
                self.methods = conf[RightNowSOAP.__name__]['methods']
        else:
            LOGGER.error("Error initializing RightNow SOAP client configuration file not found")
            raise Exception("Error initializing RightNow SOAP client configuration file not found")

        super().__init__(self.host, self.wsdl_url, self.soap_url, self.wsdl, self.methods, None)
        self.set_security_token(self.username, self.password)

        LOGGER.info("RightNow SOAP client ready")

    def update_account(self, id, login=None, display_name=None):
        """Performs an account update."""

        LOGGER.info("Performing account update ID: [%s]" % id)
        try:
            self.set_client_info_header('Basic Update')
            self.client.options.plugins = []
            xml_path = 'Body/UpdateResponse'

            Account = self.client.factory.create("{urn:objects.ws.rightnow.com/v1_3}Account")
            Account.ID._id = id

            if login:
                Account.Login = login
            if display_name:
                Account.DisplayName = display_name
                Account.Name.First = display_name
                Account.Name.Last = display_name

            processing_options = {
                'SuppressExternalEvents': False,
                'SuppressRules': False
            }

            resp = self.client.service.Update(Account, processing_options)
            return self.get_response_path(resp, xml_path)
        except Exception as e:
            LOGGER.error("Error update_account(() trying call service: %s" % str(e))
            raise Exception("Error update_account(() trying call service: %s" % str(e))

    def destroy_account(self, id):
        """Performs an account destroy"""

        LOGGER.info("Performing account destroy ID: [%s]" % id)
        try:
            self.set_client_info_header('Basic Destroy')
            self.client.options.plugins = []
            xml_path = 'Body/DestroyResponse'

            Account = self.client.factory.create("{urn:objects.ws.rightnow.com/v1_3}Account")
            Account.ID._id = id
            processing_options = {
                'SuppressExternalEvents': False,
                'SuppressRules': False
            }

            resp = self.client.service.Destroy(Account, processing_options)
            return self.get_response_path(resp, xml_path)
        except Exception as e:
            LOGGER.error("Error destroy_account(() trying call service: %s" % str(e))
            raise Exception("Error destroy_account(() trying call service: %s" % str(e))

    def create_account(self, login, display_name, profile_id=7, staff_group_id=100078):
        """Performs an account create"""

        LOGGER.info("Performing account create Login: [%s], DisplayName: [%s]" % (login, display_name))
        try:
            self.set_client_info_header('Basic Create')
            self.client.options.plugins = []
            xml_path = 'Body/CreateResponse/RNObjectsResult/RNObjects'

            Account = self.set_account(display_name, login, profile_id, staff_group_id)
            processing_options = {
                "SuppressExternalEvents": False,
                "SuppressRules": False
            }

            resp = self.client.service.Create(Account, processing_options)
            return self.get_response_path(resp, xml_path)
        except WebFault as w:
            if w.fault.faultstring:
                LOGGER.error("Error create_account() saving %s: %s" % (login, w.fault.faultstring))
                raise Exception("Error create_account() saving %s: %s" % (login, w.fault.faultstring))
        except Exception as e:
            LOGGER.error("Error create_account() trying call service: %s" % str(e))
            raise Exception("Error create_account() trying call service: %s" % str(e))

    def get_account(self, id):
        """
        Performs a get account
        :param id:
        :return: RightNowUser
        """
        LOGGER.info("Performing get account ID: [%s]" % id)
        response = RightNowAccount()
        try:
            self.set_client_info_header('Basic Get')
            self.client.options.plugins = []
            xml_path = 'Body/GetResponse/RNObjectsResult/RNObjects'

            Account = self.client.factory.create("{urn:objects.ws.rightnow.com/v1_3}Account")
            Account.ID._id = id
            processing_options = {"FetchAllNames": False}

            raw = self.client.service.Get(Account, processing_options)
            r = self.get_response_path(raw, xml_path)
            if r and r.__len__() > 0:
                for attributes in r[0].children:
                    if attributes.name == 'Login':
                        response.Login = str(attributes.text)
                    if attributes.name == 'DisplayName':
                        response.DisplayName = str(attributes.text)
                    if attributes.attributes.__len__() > 0 and attributes.attributes[0].name == 'id':
                        response.ID = int(attributes.attributes[0].value)
            return response
        except WebFault as w:
            if "Invalid ID" in w.fault.faultstring:
                LOGGER.error("Error get_account(): %s" % w.fault.faultstring)
                raise Exception("Error get_account(): %s" % w.fault.faultstring)
            else:
                return response
        except Exception as e:
            LOGGER.error("Error get_account() trying call service: %s" % str(e))
            raise Exception("Error get_account() trying call service: %s" % str(e))

    def get_query_csv(self, query='SELECT A.ID, A.Login, A.DisplayName FROM Account A', page_size=10000):
        """
        Performs get accounts CSV
        :param query:
        :param page_size:
        :return: List of users with comma separated attributes
        """
        LOGGER.info("Performing get account CSV Query: [%s]" % query)
        try:
            self.set_client_info_header('Basic Query CSV')
            self.client.options.plugins = []
            xml_path = 'Body/QueryCSVResponse/CSVTableSet/CSVTables/CSVTable/Rows/Row'
            resp = self.get_response_path(self.client.service.QueryCSV(query, page_size), xml_path)
            response = []
            if resp and resp.__len__() > 0:
                for user in resp:
                    user = str(user.text).split(',')
                    if user.__len__() > 2:
                        rightnow_user = RightNowAccount(int(user[0]), user[1], user[2])
                        response.append(rightnow_user)
            return response
        except Exception as e:
            LOGGER.error("Error get_query_csv() trying call service: %s" % str(e))
            raise Exception("Error get_query_csv() trying call service: %s" % str(e))

    def set_client_info_header(self, header):
        try:
            client_info_header = self.client.factory.create("{urn:messages.ws.rightnow.com/v1_3}ClientInfoHeader")
            client_info_header.AppID = header
            self.set_headers(client_info_header)
        except Exception as e:
            LOGGER.error("Error set_client_info_header(): %s" % str(e))
            raise Exception("Error set_client_info_header(): %s" % str(e))

    def set_account(self, display_name, login, profile_id, staff_group_id):

        password = 'Or4cl32015'
        Account = self.client.factory.create("{urn:objects.ws.rightnow.com/v1_3}Account")
        Account.DisplayName = display_name
        Account.Login = login
        Account.Name.First = display_name
        Account.Name.Last = display_name
        Account.Profile.ID._id = profile_id
        Account.NewPassword = password
        Account.StaffGroup.ID._id = staff_group_id

        return Account
