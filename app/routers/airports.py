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


@router.get("/", response_model=list(AirportRead), summary="Airports List")
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
