from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import Person, DailyEgg, DailyEggPerson


# ================= PEOPLE =================
def add_person(db: Session, name: str):
    if not name.strip():
        raise ValueError("Name required")

    exists = db.query(Person).filter(Person.name == name).first()
    if exists:
        raise ValueError("Person already exists")

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
    return person


def delete_person(db: Session, person_id: int):
    used = db.query(DailyEggPerson)\
        .filter(DailyEggPerson.person_id == person_id)\
        .first()

    if used:
        raise ValueError("Cannot delete person with history")

    person = get_person(db, person_id)
    db.delete(person)
    db.commit()


# ================= RECHARGE =================
def recharge_person(db: Session, person_id: int, amount: float):
    if amount <= 0:
        raise ValueError("Invalid amount")

    person = get_person(db, person_id)
    person.balance += amount
    db.commit()

    return {
        "name": person.name,
        "balance": round(person.balance, 2)
    }


def clear_person_balance(db: Session, person_id: int):
    person = get_person(db, person_id)
    person.balance = 0
    db.commit()
    return {"message": "Balance cleared", "balance": 0}


# 🆕 CLEAR ONLY DUE (NEGATIVE -> 0)
def clear_due(db: Session, person_id: int):
    person = get_person(db, person_id)

    if person.balance >= 0:
        return {
            "message": "No due to clear",
            "balance": round(person.balance, 2)
        }

    person.balance = 0
    db.commit()

    return {
        "message": f"{person.name} due cleared",
        "balance": 0
    }


# ================= DAILY EGGS =================
def add_daily_eggs(db: Session, data):
    if db.query(DailyEgg).filter(DailyEgg.date == data["date"]).first():
        raise ValueError("Daily entry already exists for this date")

    total_eggs = sum(data["eggs"].values())
    if total_eggs == 0:
        raise ValueError("No eggs entered")

    total_cost = total_eggs * data["egg_price"]

    record = DailyEgg(
        date=data["date"],
        egg_price=data["egg_price"],
        total_eggs=total_eggs,
        total_cost=total_cost
    )
    db.add(record)
    db.flush()

    for pid, eggs in data["eggs"].items():
        if eggs <= 0:
            continue

        person = get_person(db, pid)
        share = (eggs / total_eggs) * total_cost

        person.total_eggs += eggs
        person.total_amount += share
        person.balance -= share

        db.add(DailyEggPerson(
            daily_egg_id=record.id,
            person_id=pid,
            eggs=eggs,
            amount=share
        ))

    db.commit()
    return {
        "message": "Daily eggs added",
        "total_cost": round(total_cost, 2)
    }


def list_daily_eggs(db: Session):
    return db.query(DailyEgg).order_by(DailyEgg.date.desc()).all()


def undo_last_daily_eggs(db: Session):
    last = db.query(DailyEgg).order_by(DailyEgg.id.desc()).first()
    if not last:
        raise ValueError("No daily entry to undo")

    for entry in last.entries:
        person = get_person(db, entry.person_id)
        person.total_eggs -= entry.eggs
        person.total_amount -= entry.amount
        person.balance += entry.amount

    db.delete(last)
    db.commit()
    return {"message": "Last daily entry undone"}


# ================= REPORTS =================
def person_history(db: Session, person_id: int):
    get_person(db, person_id)

    rows = (
        db.query(DailyEgg, DailyEggPerson)
        .join(DailyEggPerson)
        .filter(DailyEggPerson.person_id == person_id)
        .order_by(DailyEgg.date.desc())
        .all()
    )

    return [
        {
            "date": d.date,
            "eggs": e.eggs,
            "amount": round(e.amount, 2),
            "egg_price": d.egg_price
        }
        for d, e in rows
    ]


def get_due_report(db: Session):
    return {
        p.name: round(abs(p.balance), 2)
        for p in db.query(Person).all()
        if p.balance < 0
    }


def get_total_balance(db: Session):
    people = db.query(Person).all()
    credit = sum(p.balance for p in people if p.balance > 0)
    due = sum(abs(p.balance) for p in people if p.balance < 0)

    return {
        "total_credit": round(credit, 2),
        "total_due": round(due, 2),
        "net_balance": round(credit - due, 2)
    }

# ================= CLEAR ALL DUES =================
def clear_all_dues(db: Session):
    people = db.query(Person).all()
    count = 0

    for p in people:
        if p.balance < 0:
            p.balance = 0
            count += 1

    db.commit()

    return {
        "message": "All dues cleared successfully",
        "cleared_users": count
    }


# ================= CLEAR =================
def clear_daily_history(db: Session):
    db.query(DailyEggPerson).delete()
    db.query(DailyEgg).delete()
    db.commit()
    return {"message": "Daily history cleared"}


def clear_database(db: Session):
    db.query(DailyEggPerson).delete()
    db.query(DailyEgg).delete()
    db.query(Person).delete()
    db.commit()
    return {"message": "Database cleared completely"}

