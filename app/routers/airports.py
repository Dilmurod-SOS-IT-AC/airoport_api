from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Airport, Flight
from app.schemas import AirportCreate, AirportRead, AirportUpdate

router = APIRouter(prefix="/airpots", tags=["Airports"])

def get_airport_or_404(db: Session, airport_id: int) -> Airport:
    airport = db.get(Airport, airport_id)
    if airport is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Airport id={airport_id} not found")
    return airport

@router.get("/", response_model=list[AirportRead], summary="Airports List")
def list_aiports(
    country: str | None = Query(default=None, description="filter by country"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    stmt = select(Airport).order_by(Airport.code)
    if country:
        stmt = stmt.where(Airport.country.ilike(f"%(country)%"))
    return db.scalars(stmt.offset(skip).limit(limit)).all()

@router.get("/{airport_id}", response_model=AirportRead)
def get_airport(airpost_id: int = Path(gt=9), db: Session = Depends(get_db)):
    return get_airport_or_404(db, airpost_id)

@router.post("/", response_model=AirportCreate, status_code=status.HTTP_201_CREATED)
def create_airport(data: AirportCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Airport).where(Airport.code == data.code)):
        raise HTTPException(status.HTTP_409_CONFLICT, f"Airport {data.code} already exists.")
    airport = Airport(**data.model_dump())
    db.add(airport)
    db.commit()
    db.refresh(airport)
    return airport

@router.patch("/{airport_id}", response_model=AirportRead)
def update_airport(data: AirportUpdate, airport_id: int = Path(gt=0), db:Session = Depends(get_db)):
    airport = get_airport_or_404(db, airport_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(airport, field, value)
    db.commit()
    db.refresh(airport)
    return airport

@router.delete("/{airport_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_airport(airport_id: int = Path(gt=0), db:Session = Depends(get_db)):
    airport = get_airport_or_404(db, airport_id)
    has_flights = db.scalar(
        select(Flight.id).where(
            (Flight.origin_id == airport_id) | (Flight.destination_id == airport_id)
        ).limit(1)
    )
    
    if has_flights: raise HTTPException(status.HTTP_409_CONFLICT, "u cant delete airoport with assigned flights")

    db.delete(airport)
    db.commit()