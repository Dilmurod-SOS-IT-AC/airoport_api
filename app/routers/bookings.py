from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Booking
from app.pricing import get_ticket_price
from app.routers.flights import get_flight_or_404
from app.schemas import BookingCreate, BookingRead, PricePreview, SeatClass

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


def get_booking_or_404(db: Session, booking_id: int) -> Booking:
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Бронь id={booking_id} не найдена")
    return booking


@router.get("/", response_model=list[BookingRead], summary="Список бронирований")
def list_bookings(
    flight_id: int | None = Query(default=None, gt=0, description="Только этот рейс"),
    passport_number: str | None = Query(default=None, description="Брони пассажира"),
    db: Session = Depends(get_db),
):
    stmt = select(Booking).order_by(Booking.id)
    if flight_id:
        stmt = stmt.where(Booking.flight_id == flight_id)
    if passport_number:
        stmt = stmt.where(Booking.passport_number == passport_number.upper())
    return db.scalars(stmt).all()


# Фиксированный путь — ВЫШЕ, чем /{booking_id}
@router.get("/price-preview", response_model=PricePreview, summary="Узнать цену билета")
def price_preview(
    flight_id: int = Query(gt=0),
    seat_class: SeatClass = Query(default=SeatClass.economy),
    db: Session = Depends(get_db),
):
    flight = get_flight_or_404(db, flight_id)
    return PricePreview(
        flight_number=flight.flight_number,
        seat_class=seat_class,
        base_price=flight.base_price,
        final_price=get_ticket_price(seat_class, flight.base_price),
    )


@router.get("/{booking_id}", response_model=BookingRead, summary="Бронь по id")
def get_booking(booking_id: int = Path(gt=0), db: Session = Depends(get_db)):
    return get_booking_or_404(db, booking_id)


@router.post("/", response_model=BookingRead, status_code=status.HTTP_201_CREATED,
             summary="Забронировать билет")
def create_booking(data: BookingCreate, db: Session = Depends(get_db)):
    flight = get_flight_or_404(db, data.flight_id)

    if flight.available_seats <= 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "На рейсе нет свободных мест")

    already_booked = db.scalar(
        select(Booking).where(Booking.flight_id == flight.id,
                              Booking.passport_number == data.passport_number)
    )
    if already_booked:
        raise HTTPException(status.HTTP_409_CONFLICT,
                            "Этот пассажир уже забронировал этот рейс")

    booking = Booking(
        flight_id=flight.id,
        passenger_name=data.passenger_name,
        passport_number=data.passport_number,
        seat_class=data.seat_class.value,
        price=get_ticket_price(data.seat_class, flight.base_price),  # ООП-расчёт
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Отменить бронь")
def cancel_booking(booking_id: int = Path(gt=0), db: Session = Depends(get_db)):
    booking = get_booking_or_404(db, booking_id)
    db.delete(booking)
    db.commit()