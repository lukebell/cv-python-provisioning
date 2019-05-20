"""
Python Exception
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# CVProvisioningException.py
__author__ = "Lucas Campana Levy"
__email__ = 'lcampana@cablevsion.com.ar'
__version__ = (0, 1, 0)
__written_date__ = "12-10-2015:Thursday"
__title__ = "Cablevision Provisioning Exception"


class CVProvisioningException(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(CVProvisioningException, self).__init__(message)

        # For custom code
        self.message = message
