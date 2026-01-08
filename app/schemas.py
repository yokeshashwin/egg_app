from pydantic import BaseModel
from typing import Dict
from datetime import date


# -------- WALLET --------
class WalletCreate(BaseModel):
    amount: float


class WalletRecharge(BaseModel):
    amount: float


# -------- PEOPLE --------
class PersonCreate(BaseModel):
    name: str


class PersonUpdate(BaseModel):
    name: str


# -------- DAILY EGGS --------
class DailyEggEntry(BaseModel):
    date: date
    egg_price: float
    eggs: Dict[int, int]  # person_id -> eggs
