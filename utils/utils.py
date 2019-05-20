"""
utils common module
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# utils.py
__author__ = "Lucas Campana Levy"
__email__ = 'lcampana@cablevsion.com.ar'
__version__ = (0, 1, 0)
__written_date__ = "09-10-2015:Thursday"
__title__ = "Utils common module"

import json


def convert_dict_to_utf8(dictionary):
    """
    Recursively converts dictionary keys to strings.
    :param dictionary:
    :return dict with keys / values converted
    """

    if not isinstance(dictionary, dict):
        return dictionary
    return dict({str(key.decode('utf-8')): str(value.decode('utf-8')) for key, value in dictionary.items()})


def convert_dict_to_json(dictionary):
    """
    Converts dictionary to a JSON
    :param dictionary:
    :return: JSON Object
    """

    if isinstance(dictionary, dict):
        return json.loads(json.dumps(dictionary))
    else:
        return json.loads("{}")
