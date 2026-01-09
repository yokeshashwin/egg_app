from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, SessionLocal
from app import services, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Egg Counting App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= PEOPLE =================
@app.post("/people")
def add_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    try:
        return services.add_person(db, person.name)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/people")
def list_people(db: Session = Depends(get_db)):
    return services.list_people(db)


@app.get("/people/{person_id}")
def get_person(person_id: int, db: Session = Depends(get_db)):
    try:
        return services.get_person(db, person_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@app.put("/people/{person_id}")
def update_person(person_id: int, person: schemas.PersonUpdate, db: Session = Depends(get_db)):
    return services.update_person(db, person_id, person.name)


@app.delete("/people/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db)):
    try:
        services.delete_person(db, person_id)
        return {"message": "Deleted"}
    except ValueError as e:
        raise HTTPException(400, str(e))


# ================= RECHARGE =================
@app.post("/people/{person_id}/recharge")
def recharge_person(person_id: int, body: schemas.RechargeAmount, db: Session = Depends(get_db)):
    try:
        return services.recharge_person(db, person_id, body.amount)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.post("/people/{person_id}/clear-balance")
def clear_person_balance(person_id: int, db: Session = Depends(get_db)):
    return services.clear_person_balance(db, person_id)


# 🆕 CLEAR DUE API
@app.post("/people/{person_id}/clear-due")
def clear_due(person_id: int, db: Session = Depends(get_db)):
    try:
        return services.clear_due(db, person_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


# ================= DAILY EGGS =================
@app.post("/daily-eggs")
def daily_eggs(entry: schemas.DailyEggEntry, db: Session = Depends(get_db)):
    try:
        return services.add_daily_eggs(db, entry.dict())
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.post("/daily-eggs/undo")
def undo_daily_eggs(db: Session = Depends(get_db)):
    try:
        return services.undo_last_daily_eggs(db)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/reports/daily-eggs")
def daily_eggs_report(db: Session = Depends(get_db)):
    return services.list_daily_eggs(db)


# ================= REPORTS =================
@app.get("/people/{person_id}/history")
def person_history(person_id: int, db: Session = Depends(get_db)):
    return services.person_history(db, person_id)


@app.get("/reports/dues")
def dues(db: Session = Depends(get_db)):
    return services.get_due_report(db)

# ================= CLEAR ALL DUES =================
@app.post("/admin/clear-all-dues")
def clear_all_dues(db: Session = Depends(get_db)):
    return services.clear_all_dues(db)


@app.get("/reports/total-balance")
def total_balance(db: Session = Depends(get_db)):
    return services.get_total_balance(db)


# ================= ADMIN =================
@app.delete("/daily-eggs/clear")
def clear_daily(db: Session = Depends(get_db)):
    return services.clear_daily_history(db)


@app.delete("/admin/clear-db")
def clear_db(db: Session = Depends(get_db)):
    return services.clear_database(db)

