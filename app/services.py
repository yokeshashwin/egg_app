from sqlalchemy.orm import Session
from app.models import Wallet, Person, DailyEgg


# ---------------- WALLET ----------------
def get_wallet(db: Session):
    wallet = db.query(Wallet).first()
    if not wallet:
        wallet = Wallet(balance=0)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet


def create_wallet(db: Session, amount: float):
    wallet = get_wallet(db)
    wallet.balance = amount
    db.commit()
    return wallet


def recharge_wallet(db: Session, amount: float):
    wallet = get_wallet(db)
    wallet.balance += amount
    db.commit()
    return wallet


# ---------------- PEOPLE ----------------
def add_person(db: Session, name: str):
    person = Person(name=name)
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


def list_people(db: Session):
    return db.query(Person).all()


def get_person(db: Session, person_id: int):
    person = db.get(Person, person_id)
    if not person:
        raise ValueError("Person not found")
    return person


def update_person(db: Session, person_id: int, name: str):
    person = get_person(db, person_id)
    person.name = name
    db.commit()
    db.refresh(person)
    return person


def delete_person(db: Session, person_id: int):
    person = get_person(db, person_id)
    db.delete(person)
    db.commit()


# ---------------- DAILY EGGS ----------------
def add_daily_eggs(db: Session, data):
    wallet = get_wallet(db)

    total_eggs = sum(data["eggs"].values())
    total_cost = total_eggs * data["egg_price"]

    if total_cost > wallet.balance:
        raise ValueError("Insufficient wallet balance")

    for pid, eggs in data["eggs"].items():
        person = get_person(db, pid)
        share = (eggs / total_eggs) * total_cost
        person.total_eggs += eggs
        person.total_amount += share

    wallet.balance -= total_cost

    record = DailyEgg(
        date=data["date"],
        egg_price=data["egg_price"],
        total_eggs=total_eggs,
        total_cost=total_cost
    )

    db.add(record)
    db.commit()

    return {
        "total_eggs": total_eggs,
        "total_cost": total_cost,
        "wallet_balance": wallet.balance
    }


def list_daily_eggs(db: Session):
    return db.query(DailyEgg).order_by(DailyEgg.date.desc()).all()


# ---------------- RECHARGE SPLIT ----------------
def recharge_split(db: Session, amount: float):
    people = db.query(Person).all()
    total_eggs = sum(p.total_eggs for p in people)

    if total_eggs == 0:
        return {}

    return {
        p.name: round((p.total_eggs / total_eggs) * amount, 2)
        for p in people
    }

# ---------------- UNDO LAST DAILY ENTRY ----------------
def undo_last_daily_eggs(db: Session):
    last = db.query(DailyEgg).order_by(DailyEgg.id.desc()).first()
    if not last:
        raise ValueError("No daily entry to undo")

    wallet = get_wallet(db)
    people = db.query(Person).all()

    total_eggs = sum(p.total_eggs for p in people)
    if total_eggs == 0:
        raise ValueError("Invalid state")

    # rollback people
    for p in people:
        ratio = p.total_eggs / total_eggs
        eggs_rollback = ratio * last.total_eggs
        amount_rollback = ratio * last.total_cost

        p.total_eggs -= round(eggs_rollback)
        p.total_amount -= amount_rollback

        if p.total_eggs < 0:
            p.total_eggs = 0
        if p.total_amount < 0:
            p.total_amount = 0

    # rollback wallet
    wallet.balance += last.total_cost

    # delete record
    db.delete(last)
    db.commit()

    return {
        "message": "Last daily entry undone",
        "wallet_balance": wallet.balance
    }

# ---------------- CLEAR DAILY HISTORY ----------------
def clear_daily_history(db: Session):
    db.query(DailyEgg).delete()
    db.commit()
    return {"message": "Daily egg history cleared"}

# ---------------- CLEAR ENTIRE DATABASE ----------------
def clear_database(db: Session):
    db.query(DailyEgg).delete()
    db.query(Person).delete()
    db.query(Wallet).delete()
    db.commit()
    return {"message": "Database cleared completely"}

# ---------------- CLEAR WALLET ----------------
def clear_wallet(db: Session):
    wallet = get_wallet(db)
    wallet.balance = 0
    db.commit()
    db.refresh(wallet)
    return {
        "message": "Wallet balance cleared",
        "balance": wallet.balance
    }
