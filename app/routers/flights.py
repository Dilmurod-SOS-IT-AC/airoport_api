from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, aliased, selectinload

from app.database import get_db
from app.models import Airport, Flight
from app.schemas import FlightCreate, FlightRead, FlightUpdate

router = APIRouter(prefix="/flights", tags=["Рейсы"])

FLIGHT_LOAD = (
    selectinload(Flight.origin),
    selectinload(Flight.destination),
    selectinload(Flight.bookings),
)


def get_flight_or_404(db: Session, flight_id: int) -> Flight:
    flight = db.scalar(select(Flight).options(*FLIGHT_LOAD).where(Flight.id == flight_id))
    if flight is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Рейс id={flight_id} не найден")
    return flight


@router.get("/", response_model=list[FlightRead], summary="Поиск рейсов")
def list_flights(
    origin: str | None = Query(default=None, description="Код аэропорта вылета, напр. TAS"),
    destination: str | None = Query(default=None, description="Код аэропорта прилёта, напр. IST"),
    on_date: date | None = Query(default=None, description="Дата вылета, ГГГГ-ММ-ДД"),
    db: Session = Depends(get_db),
):
    Origin = aliased(Airport)
    Destination = aliased(Airport)
    stmt = (
        select(Flight)
        .join(Origin, Flight.origin_id == Origin.id)
        .join(Destination, Flight.destination_id == Destination.id)
        .options(*FLIGHT_LOAD)
        .order_by(Flight.departure_time)
    )
    if origin:
        stmt = stmt.where(Origin.code == origin.upper())
    if destination:
        stmt = stmt.where(Destination.code == destination.upper())
    if on_date:
        day_start = datetime.combine(on_date, time.min)
        stmt = stmt.where(Flight.departure_time >= day_start,
                          Flight.departure_time < day_start + timedelta(days=1))
    return db.scalars(stmt).all()


@router.get("/{flight_id}", response_model=FlightRead)
def get_flight(flight_id: int = Path(gt=0), db: Session = Depends(get_db)):
    return get_flight_or_404(db, flight_id)


@router.post("/", response_model=FlightRead, status_code=status.HTTP_201_CREATED,
             summary="Создать рейс")
def create_flight(data: FlightCreate, db: Session = Depends(get_db)):
    for airport_id in (data.origin_id, data.destination_id):
        if db.get(Airport, airport_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Airport id={airport_id} not found")
    if db.scalar(select(Flight).where(Flight.flight_number == data.flight_number)):
        raise HTTPException(status.HTTP_409_CONFLICT,
                            f"Flight {data.flight_number} already exists")
    flight = Flight(**data.model_dump())
    db.add(flight)
    db.commit()
    return get_flight_or_404(db, flight.id)

@router.patch("/{flight_id}", response_model=FlightRead)
def update_flight(data: FlightUpdate, flight_id: int = Path(gt=0),
                  db: Session = Depends(get_db)):
    flight = get_flight_or_404(db, flight_id)
    changes = data.model_dump(exclude_unset=True)

    new_departure = changes.get("departure_time", flight.departure_time)
    new_arrival = changes.get("arrival_time", flight.arrival_time)
    if new_arrival <= new_departure:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "departure time must be earlier than departure time")
    if "total_seats" in changes and changes["total_seats"] < len(flight.bookings):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            f"Already sold {len(flight.bookings)}")

    for field, value in changes.items():
        setattr(flight, field, value)
    db.commit()
    return get_flight_or_404(db, flight_id)


@router.delete("/{flight_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flight(flight_id: int = Path(gt=0), db: Session = Depends(get_db)):
    flight = get_flight_or_404(db, flight_id)
    db.delete(flight)  # cascade
    db.commit()