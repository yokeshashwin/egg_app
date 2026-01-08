from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from app.database import Base

class Wallet(Base):
    __tablename__ = "wallet"
    id = Column(Integer, primary_key=True)
    balance = Column(Float, default=0)


class Person(Base):
    __tablename__ = "people"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    total_eggs = Column(Integer, default=0)
    total_amount = Column(Float, default=0)


class DailyEgg(Base):
    __tablename__ = "daily_eggs"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    egg_price = Column(Float)
    total_eggs = Column(Integer)
    total_cost = Column(Float)
