import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from email.utils import formataddr
from email.header import Header


class Mailer(object):
    def __init__(self, params):
        try:
            self.smtpObj = smtplib.SMTP()
            self.smtpObj.connect(params["smtp_host"], params["smtp_port"])
            self.smtpObj.login(params["smtp_user"], params["smtp_password"])
        except Exception as e:
            logging.error(str(e))

    def __del__(self):
        try:
            self.smtpObj.close()
        except Exception as e:
            logging.error(str(e))

    def send_mail(self, task):
        msg = MIMEMultipart()
        msg["From"] = formataddr((Header(task.task_show_name, 'utf-8').encode(), task.task_from_address))
        msg["To"] = task.task_to_address
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = Header(task.task_subject, 'utf-8').encode()
        msg.attach(MIMEText(task.task_body, 'html'))
        if task.task_atts:
            att_files = task.task_atts.split("|")
            for att_file in att_files:
                att = MIMEBase('application', "octet-stream", filename=Header(att_file, 'utf-8').encode())
                att.set_payload(open("attachments/{}".format(att_file), "rb").read())
                encoders.encode_base64(att)
                att.add_header("Content-Disposition", "attachment", filename=Header(att_file, 'utf-8').encode())
                msg.attach(att)
        self.smtpObj.sendmail(task.task_from_address, task.task_to_address, msg.as_string())
