"""
SOAP client module
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# soap.py
__author__ = "Lucas Campana Levy"
__email__ = 'lcampana@cablevsion.com.ar'
__version__ = (0, 1, 0)
__written_date__ = "09-10-2015:Thursday"
__title__ = "SOAP client module"

import requests
from suds.client import Client
from suds.xsd.doctor import Import, ImportDoctor
from suds.sax.parser import Parser
from suds.wsse import *


class SOAPClient:
    """
    Pass any kwargs to init that you would to the suds.client.Client constructor.
    A little bit of magic is performed with the ImportDoctor to cover missing
    types used in the WSDL.
        * If you specify wsdl, this file will be pulled from the default http URL
        * If you specify wsdl_url, it will override the wsdl file. Local
         "file://" URLs work just fine.
        * If you do not specify autosave, it will be enabled by default for
          volatile operations.
    To save time for re-usable code, it is a good idea subclassing this to
    create methods for commonly used commands in your application.
    """

    def __init__(self, host=None, wsdl_url=None, soap_url=None, wsdl=None, read_only_commands=None, autosave=True,
                 **kwargs):
        """
        Creates the suds.client.Client object and loads the WSDL.
        Pass autosave=False to disable the auto-save feature.
        """
        self.host = host
        self.wsdl = wsdl
        self.wsdl_url = wsdl_url or self.host + self.wsdl
        self.soap_url = soap_url or self.host
        self.read_only_commands = read_only_commands
        self.autosave = autosave

        # Fix missing types with ImportDoctor, otherwise we get:
        # suds.TypeNotFound: Type not found: '(Array, # http://schemas.xmlsoap.org/soap/encoding/, )
        self._import = Import('http://schemas.xmlsoap.org/soap/encoding/')
        self._import.filter.add("urn:NSConfig")
        self.doctor = ImportDoctor(self._import)

        for key, value in kwargs.items():
            # set attributes, but don't reset explicit ones.
            if not hasattr(self, key):
                setattr(self, key, value)

        self.client = Client(self.wsdl_url, doctor=self.doctor, location=self.soap_url, retxml=True, **kwargs)
        self.config_changed = False
        self.logged_in = False

    def __str__(self):
        """client to string"""
        return str(self.client)

    @property
    def service(self):
        return self.client.service

    def is_readonly(self, cmd):
        """Validates whether a command is read-only based on READONLY_COMMANDS"""
        ret = False
        for roc in self.read_only_commands:
            if cmd.startswith(roc):
                ret = True
        return ret

    @staticmethod
    def get_wsdl(url, filename):

        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(filename, 'wb') as output:
                for chunk in r.iter_content(1024):
                    output.write(chunk)

    def set_headers(self, headers):
        """
        Sets client headers
        :param headers:
        :return:
        """

        if headers:
            self.client.set_options(soapheaders=headers)

    def set_security_token(self, username, password):
        """
        Sets security token
        :param username:
        :param password:
        :return:
        """

        security = Security()
        token = UsernameToken(username, password)
        s = [username, password, str(datetime.utcnow().replace(tzinfo=UtcTimezone()))]
        m = md5()
        m.update(':'.join(s).encode('utf-8'))
        token.setnonce(m.hexdigest())
        token.setcreated()
        security.tokens.append(token)
        self.client.set_options(wsse=security)

    @staticmethod
    def get_response_path(response, xml_path):
        """
        Formats the response
        :param response:
        :return: The xml path given
        """
        if response and xml_path:
            sax = Parser()
            res = sax.parse(string=response)
            return res._Document__root.childrenAtPath(xml_path)
