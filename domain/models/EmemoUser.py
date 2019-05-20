"""
Ememo user model
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# EmemoUser.py
__author__ = "Lucas Campana Levy"
__email__ = 'lcampana@cablevsion.com.ar'
__version__ = (0, 1, 0)
__written_date__ = "12-10-2015:Thursday"
__title__ = "Ememmo user model"


class EmemoUser:
    EMEMO_BASE = 'Ememo/'
    user_id = None
    nombre = None
    apellido = None
    nick = None
    nombre_sector = None
    nom_udn = None
    nom_site = None
    ultimo_login = None

    @property
    def base_login(self):
        return self.EMEMO_BASE + self.nick

    @property
    def display_name(self):
        return self.nombre + ' ' + self.apellido

    def __init__(self, userId=None, nombre=None, apellido=None, nick=None, nombreSector=None, nomUdn=None, nomSite=None,
                 ultimoLogin=None):
        """
        Default constructor

        :param userId:
        :param nombre:
        :param apellido:
        :param nick:
        :param nombreSector:
        :param nomUdn:
        :param nomSite:
        :param ultimoLogin:
        :return:
        """

        self.user_id = userId
        self.nombre = nombre
        self.apellido = apellido
        self.nick = nick
        self.nombre_sector = nombreSector
        self.nom_udn = nomUdn
        self.nom_site = nomSite
        self.ultimo_login = ultimoLogin
