from datetime import date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Numeric


Base = declarative_base()


class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    title = Column(String)
    price_usd = Column(Numeric(10, 2))
    odometer = Column(Integer)
    username = Column(String)
    phone_number = Column(Integer)
    image_url = Column(String)
    images_count = Column(Integer)
    car_number = Column(String)
    car_vin = Column(String)
    datetime_found = Column(Date, default=date.today)
