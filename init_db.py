import db_utils
import getpass
import os


smtp_host = input("SMTP server host:")
smtp_port = input("SMTP server port:")
smtp_user = input("SMTP user:")
smtp_password = getpass.getpass("SMTP password:")
admin_user = input("Administrator username:")
admin_password = getpass.getpass("Administrator password:")

db_utils.Base.metadata.create_all(db_utils.engine)
sess = db_utils.get_session()
sess.add(db_utils.Config(config_key="smtp_host", config_value=smtp_host))
sess.add(db_utils.Config(config_key="smtp_port", config_value=smtp_port))
sess.add(db_utils.Config(config_key="smtp_user", config_value=smtp_user))
sess.add(db_utils.Config(config_key="smtp_password", config_value=smtp_password))
sess.add(db_utils.Config(config_key="admin_user", config_value=admin_user))
sess.add(db_utils.Config(config_key="admin_password", config_value=admin_password))
sess.commit()
sess.close()

os.mkdir("attachments")
