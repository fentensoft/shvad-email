from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.sqlite import INTEGER, TEXT, VARCHAR
from sqlalchemy import Column, create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = create_engine("sqlite:///app.db")
DBSession = sessionmaker(bind=engine)


class Config(Base):
    __tablename__ = "tbl_config"

    id = Column(INTEGER, primary_key=True)
    config_key = Column(VARCHAR(30), unique=True)
    config_value = Column(VARCHAR(100))


class Task(Base):
    __tablename__ = "tbl_task"

    id = Column(INTEGER, primary_key=True)
    task_show_name = Column(VARCHAR(20))
    task_from_address = Column(VARCHAR(100))
    task_to_address = Column(VARCHAR(100))
    task_subject = Column(VARCHAR(100))
    task_body = Column(TEXT)
    task_atts = Column(VARCHAR(100))
    task_status = Column(VARCHAR(10))
    task_msg = Column(VARCHAR(100))

    def __to_dict__(self):
        return {
            "id": self.id,
            "task_show_name": self.task_show_name,
            "task_from_address": self.task_from_address,
            "task_to_address": self.task_to_address,
            "task_subject": self.task_subject,
            "task_body": self.task_body,
            "task_atts": self.task_atts,
            "task_status": self.task_status,
            "task_msg": self.task_msg
        }


def get_session():
    return DBSession()
