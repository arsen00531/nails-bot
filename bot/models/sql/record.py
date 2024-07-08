from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
Base = declarative_base()


class Record(Base):
    __tablename__ = "record"

    index = Column(Integer, primary_key=True)
    id = Column(BigInteger)
    company_id = Column(BigInteger)
    user_id = Column(BigInteger)
    title = Column(String)
    last_notification = Column(String)
    post_notification_1 = Column(Boolean)
    post_notification_2 = Column(Boolean)
    datetime = Column(String)



