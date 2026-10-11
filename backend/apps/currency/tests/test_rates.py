from datetime import date
from decimal import Decimal

import pytest
from django.core.cache import cache

from apps.currency import services
from apps.currency.models import ExchangeRate
from apps.currency.services import RatesFetchError, current_rates, parse_cbu, update_rates

CBU_PAYLOAD = [
    {"Ccy": "USD", "Nominal": "1", "Rate": "12000.00", "Date": "10.10.2026"},
    {"Ccy": "EUR", "Nominal": "1", "Rate": "13000.00", "Date": "10.10.2026"},
    {"Ccy": "RUB", "Nominal": "1", "Rate": "150.00", "Date": "10.10.2026"},
    {"Ccy": "JPY", "Nominal": "10", "Rate": "800.00", "Date": "10.10.2026"},
]


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()


def test_parse_cbu_converts_to_units_per_usd():
    rates, rate_date = parse_cbu(CBU_PAYLOAD)

    assert rates["USD"] == 1
    assert rates["UZS"] == Decimal("12000")
    assert rates["RUB"] == Decimal("80")  # 12000 / 150
    assert rates["JPY"] == Decimal("150")  # номинал 10: 12000 / (800 / 10)
    assert rate_date == date(2026, 10, 10)


def test_parse_cbu_without_usd_fails():
    with pytest.raises(RatesFetchError):
        parse_cbu([{"Ccy": "EUR", "Nominal": "1", "Rate": "13000", "Date": "10.10.2026"}])


def test_effective_rate_uses_manual_rate_and_markup():
    rate = ExchangeRate(currency="UZS", rate=Decimal("12000"), markup_percent=Decimal("1.5"))
    assert rate.effective_rate == Decimal("12180")

    rate.manual_rate = Decimal("12500")
    assert rate.effective_rate == Decimal("12687.5")


@pytest.mark.django_db
def test_update_rates_stores_display_currencies(monkeypatch, settings):
    settings.DISPLAY_CURRENCIES = ["USD", "UZS", "RUB"]
    monkeypatch.setattr(services, "fetch_cbu_rates", lambda: parse_cbu(CBU_PAYLOAD))

    assert sorted(update_rates()) == ["RUB", "UZS"]
    assert ExchangeRate.objects.get(currency="RUB").rate == Decimal("80")
    assert not ExchangeRate.objects.filter(currency="USD").exists()


@pytest.mark.django_db
def test_update_rates_keeps_manual_settings(monkeypatch):
    ExchangeRate.objects.create(currency="UZS", rate=1, manual_rate=Decimal("12500"))
    monkeypatch.setattr(services, "fetch_cbu_rates", lambda: parse_cbu(CBU_PAYLOAD))

    update_rates()

    rate = ExchangeRate.objects.get(currency="UZS")
    assert rate.rate == Decimal("12000")
    assert rate.manual_rate == Decimal("12500")


@pytest.mark.django_db
def test_admin_change_resets_cached_rates():
    item = ExchangeRate.objects.create(currency="UZS", rate=Decimal("12000"))
    assert current_rates()["UZS"] == Decimal("12000")

    item.markup_percent = Decimal("10")
    item.save()

    assert current_rates()["UZS"] == Decimal("13200")


@pytest.mark.django_db
def test_rates_api(client):
    ExchangeRate.objects.create(currency="UZS", rate=Decimal("12000"))

    data = client.get("/api/v1/currency/rates").json()

    assert data["base"] == "USD"
    assert Decimal(data["rates"]["UZS"]) == Decimal("12000")
    assert Decimal(data["rates"]["USD"]) == 1
