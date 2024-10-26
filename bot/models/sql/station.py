from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Null
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Station(Base):
    __tablename__ = "station"

    id = Column(Integer, primary_key=True)
    coordinate_lat = Column(String)
    coordinate_lon = Column(String)
    title = Column(String)
    address = Column(String)



