from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    total_eggs = Column(Integer, default=0)
    total_amount = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)  # +credit / -due

    entries = relationship("DailyEggPerson", back_populates="person")


class DailyEgg(Base):
    __tablename__ = "daily_eggs"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, unique=True)
    egg_price = Column(Float, nullable=False)
    total_eggs = Column(Integer, nullable=False)
    total_cost = Column(Float, nullable=False)

    entries = relationship(
        "DailyEggPerson",
        back_populates="daily_egg",
        cascade="all, delete"
    )


class DailyEggPerson(Base):
    __tablename__ = "daily_egg_people"

    id = Column(Integer, primary_key=True)
    daily_egg_id = Column(Integer, ForeignKey("daily_eggs.id"))
    person_id = Column(Integer, ForeignKey("people.id"))

    eggs = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)

    daily_egg = relationship("DailyEgg", back_populates="entries")
    person = relationship("Person", back_populates="entries")
