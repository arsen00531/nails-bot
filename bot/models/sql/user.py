from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    index = Column(Integer, primary_key=True)
    id = Column(BigInteger)
    username = Column(String)
    fullname = Column(String)
    phone = Column(String)
    company_id = Column(BigInteger, default=None)
    created_at = Column(DateTime, default=datetime.now())
