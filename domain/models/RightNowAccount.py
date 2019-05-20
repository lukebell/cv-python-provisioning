"""
RightNow user model
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# RightNowAccount.py
__author__ = "Lucas Campana Levy"
__email__ = 'lcampana@cablevsion.com.ar'
__version__ = (0, 1, 0)
__written_date__ = "12-10-2015:Thursday"
__title__ = "Rightnow user model"


class RightNowAccount:
    ID = None
    Login = None
    DisplayName = None

    def __init__(self, id=None, login=None, display_name=None):
        """
        Default constructor

        :param ID:
        :param login:
        :param display_name:
        :return:
        """
        self.ID = id
        self.Login = login
        self.DisplayName = display_name
