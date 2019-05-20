import logging.handlers
import smtplib
from email.utils import formatdate
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread


class ThreadedSMTPHandler(logging.handlers.SMTPHandler):
    def __init__(self, mailhost=None, fromaddr=None, toaddrs=None, subject=None):

        self.mailhost = mailhost
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs
        self.subject = subject
        self.smtp = smtplib.SMTP(self.mailhost)

        super(ThreadedSMTPHandler, self).__init__(mailhost, fromaddr, toaddrs, subject)

    def emit(self, record):
        try:
            msg = self.set_msg(record)
            thread = Thread(target=self.send_email, args=(msg,))
            thread.start()
        except Exception as e:
            self.handleError(str(record) + ', Error: ' + str(e))

    def set_msg(self, record):

        body = "Ha ocurrido un error al intentar procesar el servicio de provisioning contra RightNow. " \
               "\nPara más detalles consulte los logs de la aplicación. \n\n"
        record_formatted = self.format(record)
        body = body + record_formatted + "\r\n"

        # create the message
        msg = MIMEMultipart()
        msg["From"] = self.fromaddr
        msg["To"] = ', '.join(self.toaddrs)
        msg["Subject"] = self.subject
        msg["Date"] = formatdate(localtime=True)
        msg.attach(MIMEText(body))

        return msg.as_string()

    def send_email(self, msg):
        self.smtp.sendmail(self.fromaddr, self.toaddrs, msg)
        self.smtp.quit()
