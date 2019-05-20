"""
CV provisioning API
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# app.py
__author__ = "Lucas Campana Levy"
__email__ = 'lcampana@cablevsion.com.ar'
__version__ = (0, 1, 0)
__written_date__ = "12-10-2015:Thursday"
__title__ = "CV provisioning API"

from utils.logger.logger import Logger
from utils.rightnow.client.RightNowSOAP import RightNowSOAP
from handlers.EmemoHandler import EmemoHandler
from apscheduler.schedulers.blocking import BlockingScheduler

LOGGER = Logger(__name__)

try:
    LOGGER.info('Starting Cablevision provisioning process.')

    scheduler = BlockingScheduler()
    rightnow = RightNowSOAP()
    ememo = EmemoHandler(rightnow)


    @scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=22)
    def ememo_job():
        ememo.run()

    scheduler.start()
except (Exception, KeyboardInterrupt, SystemExit):
    pass
