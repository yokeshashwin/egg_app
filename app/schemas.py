from pydantic import BaseModel
from typing import Dict
from datetime import date


class PersonCreate(BaseModel):
    name: str


class PersonUpdate(BaseModel):
    name: str


class RechargeAmount(BaseModel):
    amount: float


class DailyEggEntry(BaseModel):
    date: date
    egg_price: float
    eggs: Dict[int, int]
