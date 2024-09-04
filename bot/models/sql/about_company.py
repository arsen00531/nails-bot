from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class AboutCompany(Base):
    __tablename__ = "about_company"

    index = Column(Integer, primary_key=True)
    company_id = Column(BigInteger)
    url = Column(String)



