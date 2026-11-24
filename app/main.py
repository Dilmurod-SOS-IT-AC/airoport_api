from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models
from app.database import Base, engine, get_db
from app.routers import airports, flights, bookings

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Airport CLI",
    description="",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(airports.router)
app.include_router(flights.router)
app.include_router(bookings.router)

@app.get("/", tags=["ServerTest"])
def root(): return {"message": "Airport CLI is working"}

@app.get("/health", tags=["DBTest"])
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "ok"}