from datetime import datetime
from decimal import Decimal 

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base

class Airport(Base):
    __tablename__ = "airoports"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(3), unique=True, index=True)      # TAS
    name: Mapped[str] = mapped_column(String(150))
    city: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100))

class Flight(Base):
    __tablename__ = "flights"

    id: Mapped[int] = mapped_column(primary_key=True)
    flight_num: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    origin_id : Mapped[int] = mapped_column(ForeignKey("airoports.id"))
    destination_id : Mapped[int] = mapped_column(ForeignKey("airoports.id"))
    daparture_time: Mapped[datetime] = mapped_column(DateTime)
    base_price: Mapped[Decimal] = mapped_column(Numeric())
    total_sests: Mapped[int]

    origin: Mapped["Airport"] = relationship(foreign_keys=[origin_id])
    destination: Mapped["Airport"] = relationship(foreign_keys=[destination_id])
    bookings: Mapped["Booking"] = relationship(
        back_populates="flight", cascade="all, delete-orphan"
    )

    @property
    def available_seats(self) -> int:
        return self.total_sests - len(self.bookings)


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (UniqueConstraint("flight_id", "passport_num"))


    id: Mapped[int] = mapped_column(primary_key=True)
    flight_id: Mapped[int] = mapped_column(ForeignKey("flights.id"))
    passenger_name: Mapped[str] = mapped_column(String(100))
    passport_num: Mapped[str] = mapped_column(String(20))
    seat_Class: Mapped[str] = mapped_column(String(20))
    price: Mapped[Decimal] = mapped_column(Numeric())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    flight: Mapped["Flight"] = relationship(back_populates="bookings")

