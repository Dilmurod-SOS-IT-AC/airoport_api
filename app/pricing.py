from abc import ABC, abstractmethod
from decimal import ROUND_HALF_UP, Decimal

from app.schemas import SeatClass

class TicketPricing(ABC):
    multiplier: Decimal = Decimal("1.0")

    def __init__(self, base_price: Decimal):
        self._base_price = Decimal(base_price)

    @abstractmethod
    def extra_fee(self) -> Decimal: pass

    def calc(self) -> Decimal:
        price = self._base_price * self.multiplier + self.extra_fee()
        return price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

class EconomyPricing(TicketPricing):
    multiplier: Decimal = Decimal("1.0")

    def extra_fee(self) -> Decimal: return 0


class BusinessPricing(TicketPricing):
    multiplier: Decimal = Decimal("2.5")

    def extra_fee(self) -> Decimal: return Decimal("50")


class FirstPricing(TicketPricing):
    multiplier: Decimal = Decimal("4.0")

    def extra_fee(self) -> Decimal: return Decimal("150")

PRICING_BY_CLASS: dict[SeatClass, type[TicketPricing]] = {
    SeatClass.economy: EconomyPricing,
    SeatClass.business: BusinessPricing,
    SeatClass.first: FirstPricing,
}

def get_ticket_price(seat_class: SeatClass, base_price: Decimal) -> Decimal:
    pricing = PRICING_BY_CLASS[SeatClass](base_price)
    return pricing.calc()