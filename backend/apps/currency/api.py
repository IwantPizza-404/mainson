from datetime import datetime
from decimal import Decimal

from django.conf import settings
from ninja import Router, Schema

from .models import ExchangeRate
from .services import current_rates

router = Router(tags=["currency"])


class RatesOut(Schema):
    base: str
    rates: dict[str, Decimal]
    updated_at: datetime | None


@router.get("/rates", response=RatesOut)
def get_rates(request):
    """Курсы для пересчёта цен на витрине: единиц валюты за 1 USD."""
    last = ExchangeRate.objects.order_by("-updated_at").values_list("updated_at", flat=True).first()
    return {"base": settings.BASE_CURRENCY, "rates": current_rates(), "updated_at": last}
