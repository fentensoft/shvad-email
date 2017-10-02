import db_utils
import mail_utils


def run():
    sess = db_utils.get_session()
    smtp_config = dict()
    smtp_config["smtp_host"] = sess.query(db_utils.Config.config_value).filter_by(config_key="smtp_host").first()[0]
    smtp_config["smtp_port"] = sess.query(db_utils.Config.config_value).filter_by(config_key="smtp_port").first()[0]
    smtp_config["smtp_user"] = sess.query(db_utils.Config.config_value).filter_by(config_key="smtp_user").first()[0]
    smtp_config["smtp_password"] = sess.query(db_utils.Config.config_value).filter_by(config_key="smtp_password").first()[0]
    tasks = sess.query(db_utils.Task).filter_by(task_status="Queued")
    mailer = mail_utils.Mailer(smtp_config)
    for task in tasks:
        task.task_status = "Sending"
        sess.commit()
        try:
            mailer.send_mail(task)
            task.task_status = "Done"
            task.task_msg = ""
        except Exception as e:
            task.task_status = "Failed"
            task.task_msg = str(e)
        sess.commit()
