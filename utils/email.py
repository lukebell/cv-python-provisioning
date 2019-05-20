"""
Module Email Sender
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# email.py
__author__ = "Lucas Campana Levy"
__email__ = 'lcampana@cablevsion.com.ar'
__version__ = (0, 1, 0)
__written_date__ = "12-10-2015:Thursday"
__title__ = "Email sender module"

import json
import os
import smtplib
import mimetypes
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate

from utils.logger.logger import Logger

EMAIL_CONFIG_FILE = 'conf/email-conf.json'
LOGGER = Logger(__name__)


class EmailClient:
    def __init__(self, host=None, username=None, password=None):
        """
        Default constructor
        :param host:
        :param username:
        :param password:
        """
        path = os.path.join(os.getcwd(), EMAIL_CONFIG_FILE)
        if host is None and os.path.exists(path):
            with open(path, 'rt') as f:
                conf = json.load(f)

                self.server = smtplib.SMTP(conf['host'])
                self.server.ehlo()
                self.server.starttls()
                if conf['username'] is not None and conf['username'] != "" and conf['password'] is not None \
                        and conf['password'] != "":
                    self.server.login(conf['username'], conf['password'])
        else:
            self.server = smtplib.SMTP(host)
            self.server.ehlo()
            self.server.starttls()
            if username is not None and password is not None:
                self.server.login(username, password)

        self.emails = None
        self.msg = None

    def set_msg(self, body_text, subject, from_addr, to_addr, cc_addr, bcc_addr, file_to_attach=None):
        """
        Sets utils message
        :param body_text:
        :param subject:
        :param from_addr:
        :param to_addr:
        :param cc_addr:
        :param bcc_addr:
        :param file_to_attach:
        """

        path = os.path.join(os.getcwd(), EMAIL_CONFIG_FILE)
        if os.path.exists(path):
            with open(path, 'rt') as f:
                conf = json.load(f)

            if body_text is None or body_text == "":
                body_text = conf['body'] + body_text

            if subject is None or subject == "":
                subject = conf['subject']

            if from_addr is None or from_addr == "":
                from_addr = conf['fromAddress']

            if to_addr is None or to_addr == "":
                to_addr = conf['toAddress']

            cc_addr = conf['ccAddress']
            bcc_addr = conf['bccAddress']

        is_required = "param is required"
        if not body_text:
            LOGGER.error("body_text %s" % is_required)
            raise Exception("body_text %s" % is_required)
        if not from_addr:
            LOGGER.error("from_addr %s" % is_required)
            raise Exception("from_addr %s" % is_required)
        if not to_addr:
            LOGGER.error("to_addr %s" % is_required)
            raise Exception("to_addr %s" % is_required)
        if not subject:
            LOGGER.error("subject %s" % is_required)
            raise Exception("subject %s" % is_required)

        # create the message
        msg = MIMEMultipart()
        msg["From"] = from_addr
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)
        msg.attach(MIMEText(body_text))

        msg["To"] = ', '.join(to_addr)
        emails = to_addr

        if cc_addr is not None:
            msg["CC"] = ', '.join(cc_addr)
            emails += cc_addr

        if bcc_addr is not None:
            msg["BCC"] = ', '.join(bcc_addr)
            emails += bcc_addr

        if file_to_attach is not None:
            msg.attach(self.set_attachment(file_to_attach))

        self.msg = msg
        self.emails = emails

    @staticmethod
    def set_attachment(file_to_attach):
        """
        Sets type and headers of the attachment file
        :param file_to_attach:
        :return: attachment
        """

        try:
            ctype, encoding = mimetypes.guess_type(file_to_attach)
            if ctype is None or encoding is not None:
                ctype = MIMEBase('application', "octet-stream")

            maintype, subtype = ctype.split("/", 1)

            if maintype == "text":
                fp = open(file_to_attach)
                # Note: we should handle calculating the charset
                attachment = MIMEText(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == "image":
                fp = open(file_to_attach, "rb")
                attachment = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == "audio":
                fp = open(file_to_attach, "rb")
                attachment = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
            else:
                fp = open(file_to_attach, "rb")
                attachment = MIMEBase(maintype, subtype)
                attachment.set_payload(fp.read())
                fp.close()
                encoders.encode_base64(attachment)
            attachment.add_header("Content-Disposition", "attachment", filename=file_to_attach)
        except IOError:
            LOGGER.error("Error opening attachment file %s" % file_to_attach)
            raise Exception("Error opening attachment file %s" % file_to_attach)

        return attachment

    def send_email(self, body_text=None, subject=None, from_addr=None, to_addr=None, cc_addr=None, bcc_addr=None,
                   file_to_attach=None):
        """
        Sends email function
        :param body_text:
        :param subject:
        :param from_addr:
        :param to_addr:
        :param cc_addr:
        :param bcc_addr:
        :param file_to_attach:
        """

        self.set_msg(body_text, subject, from_addr, to_addr, cc_addr, bcc_addr, file_to_attach)
        self.server.sendmail(self.msg['from'], self.emails, self.msg.as_string())
        self.server.quit()
