from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator



class AirportBase(BaseModel):
    code: str = Field(pattern=r"^[A-Z]{3}$", examples=["TAS"])
    name: str = Field(min_length=2, max_length=150, examples=["Tashkent International Airport"])
    city: str = Field(min_length=2, max_length=100, examples=["Tashkent"])
    country: str = Field(min_length=2, max_length=100, examples=["Uzbekistan"])


class AirportCreate(AirportBase):
    pass


class AirportUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    country: str | None = Field(default=None, min_length=2, max_length=100)


class AirportRead(AirportBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# -------

class FlightCreate(BaseModel):
    flight_number: str = Field(pattern=r"^[A-Z0-9]{2,8}$", examples=["HY101"])
    origin_id: int = Field(gt=0, examples=[1])
    destination_id: int = Field(gt=0, examples=[3])
    departure_time: datetime = Field(examples=["2026-12-01T08:00:00"])
    arrival_time: datetime = Field(examples=["2026-12-01T11:30:00"])
    base_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2, examples=[250])
    total_seats: int = Field(gt=0, le=1000, examples=[150])

    @model_validator(mode="after")
    def check_route_and_time(self):
        """Проверка сразу нескольких полей вместе."""
        if self.origin_id == self.destination_id:
            raise ValueError("Аэропорт вылета и прилёта должны отличаться")
        if self.arrival_time <= self.departure_time:
            raise ValueError("Время прилёта должно быть позже времени вылета")
        return self


class FlightUpdate(BaseModel):
    departure_time: datetime | None = None
    arrival_time: datetime | None = None
    base_price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    total_seats: int | None = Field(default=None, gt=0, le=1000)


class FlightRead(BaseModel):
    id: int
    flight_number: str
    departure_time: datetime
    arrival_time: datetime
    base_price: Decimal
    total_seats: int
    available_seats: int
    origin: AirportRead
    destination: AirportRead

    model_config = ConfigDict(from_attributes=True)

# -------

class SeatClass(str, Enum):
    economy = "economy"
    business = "business"
    first = "first"


class BookingCreate(BaseModel):
    flight_id: int = Field(gt=0, examples=[1])
    passenger_name: str = Field(min_length=2, max_length=100, examples=["Dilmurod Nabiev"])
    passport_number: str = Field(pattern=r"^[A-Z0-9]{6,20}$", examples=["AA1234567"])
    seat_class: SeatClass = SeatClass.economy


class BookingRead(BaseModel):
    id: int
    flight_id: int
    passenger_name: str
    passport_number: str
    seat_class: SeatClass
    price: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PricePreview(BaseModel):
    flight_number: str
    seat_class: SeatClass
    base_price: Decimal
    final_price: Decimal