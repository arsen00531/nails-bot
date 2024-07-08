from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
Base = declarative_base()


class YandexCompany(Base):
    __tablename__ = "yandex_company"

    index = Column(Integer, primary_key=True)
    company_id = Column(BigInteger)
    url = Column(String)



