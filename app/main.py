from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app import services, schemas
from fastapi.middleware.cors import CORSMiddleware

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


# -------- WALLET --------
@app.post("/wallet/create")
def create_wallet(wallet: schemas.WalletCreate, db: Session = Depends(get_db)):
    return services.create_wallet(db, wallet.amount)


@app.post("/wallet/recharge")
def recharge_wallet(wallet: schemas.WalletRecharge, db: Session = Depends(get_db)):
    return services.recharge_wallet(db, wallet.amount)


@app.get("/wallet")
def wallet_status(db: Session = Depends(get_db)):
    return services.get_wallet(db)


# -------- PEOPLE (FULL CRUD) --------
@app.post("/people")
def add_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    return services.add_person(db, person.name)


@app.get("/people")
def list_people(db: Session = Depends(get_db)):
    return services.list_people(db)


@app.get("/people/{person_id}")
def get_person(person_id: int, db: Session = Depends(get_db)):
    try:
        return services.get_person(db, person_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/people/{person_id}")
def update_person(
    person_id: int,
    person: schemas.PersonUpdate,
    db: Session = Depends(get_db)
):
    try:
        return services.update_person(db, person_id, person.name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/people/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db)):
    try:
        services.delete_person(db, person_id)
        return {"message": "Deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# -------- DAILY EGGS --------
@app.post("/daily-eggs")
def daily_eggs(entry: schemas.DailyEggEntry, db: Session = Depends(get_db)):
    try:
        return services.add_daily_eggs(db, entry.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/reports/daily-eggs")
def daily_egg_report(db: Session = Depends(get_db)):
    return services.list_daily_eggs(db)


@app.get("/reports/people-summary")
def people_summary(db: Session = Depends(get_db)):
    return services.list_people(db)


# -------- RECHARGE SPLIT --------
@app.post("/recharge-split")
def recharge_split(amount: float, db: Session = Depends(get_db)):
    return services.recharge_split(db, amount)


@app.post("/daily-eggs/undo")
def undo_daily_eggs(db: Session = Depends(get_db)):
    try:
        return services.undo_last_daily_eggs(db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/daily-eggs/clear")
def clear_daily_eggs(db: Session = Depends(get_db)):
    return services.clear_daily_history(db)


@app.delete("/admin/clear-db")
def clear_db(db: Session = Depends(get_db)):
    return services.clear_database(db)

@app.post("/wallet/clear")
def clear_wallet(db: Session = Depends(get_db)):
    return services.clear_wallet(db)
