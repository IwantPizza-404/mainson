from django.shortcuts import get_object_or_404
from django.utils.translation import get_language
from django_countries import countries
from ninja import Router, Status
from ninja.throttling import AnonRateThrottle

from apps.accounts.auth import current_customer

from .models import HOME_COUNTRY, DeliveryMethod, Order
from .schemas import (
    SUPPORTED_LANGUAGES,
    CartIn,
    CheckoutOptionsOut,
    ErrorOut,
    OrderIn,
    OrderLookupIn,
    OrderLookupOut,
    OrderOut,
    QuoteOut,
)
from .services import Customer, OrderError, build_quote, place_order

router = Router(tags=["orders"])


@router.post("/cart/quote", response=QuoteOut)
def quote_cart(request, payload: CartIn):
    """Актуальные цены и наличие для корзины (корзина хранится на клиенте)."""
    quote = build_quote(payload.as_dict())
    lines = []
    for line in quote.lines:
        product = line.product
        lines.append(
            {
                "slug": line.slug,
                "quantity": line.quantity,
                "max_quantity": line.max_quantity,
                "error": line.error,
                "name": product.name if product else None,
                "brand": product.brand.name if product else None,
                "reference": product.reference if product else None,
                "price": product.price if product else None,
                "compare_at_price": product.compare_at_price if product else None,
                "availability": product.availability if product else None,
                "lead_time_days": product.lead_time_days if product else None,
                "image": product.images.first() if product else None,
                "line_total": line.line_total,
            }
        )
    return {"lines": lines, "subtotal": quote.subtotal, "is_valid": quote.is_valid}


@router.get("/checkout/options", response=CheckoutOptionsOut)
def checkout_options(request):
    return {
        "delivery_methods": DeliveryMethod.objects.filter(is_active=True),
        "countries": [{"code": code, "name": name} for code, name in countries],
        "home_country": HOME_COUNTRY,
    }


@router.post(
    "/orders",
    response={201: OrderOut, 400: ErrorOut},
    throttle=[AnonRateThrottle("10/h")],
)
def create_order(request, payload: OrderIn):
    if payload.website:
        # Бот заполнил скрытое поле — отвечаем как обычно, но заказ не создаём
        return Status(400, {"detail": "Invalid request."})
    if payload.country not in countries:
        return Status(400, {"detail": "Unknown country."})
    language = get_language()
    try:
        order = place_order(
            items=payload.as_dict(),
            customer=Customer(
                name=payload.customer_name.strip(),
                phone=payload.phone.strip(),
                email=payload.email or "",
                contact_method=payload.contact_method,
                country=payload.country,
                city=payload.city.strip(),
                address=payload.address.strip(),
                comment=payload.comment.strip(),
            ),
            delivery_code=payload.delivery_method,
            currency=payload.currency.upper(),
            language=language if language in SUPPORTED_LANGUAGES else "en",
            account=current_customer(request),
            save_address=payload.save_address,
        )
    except OrderError as exc:
        return Status(400, {"detail": str(exc)})
    return Status(201, order)


def phone_digits(phone: str) -> str:
    # Сравниваем последние 9 цифр: «+998 90 123-45-67» и «901234567» — один номер
    return "".join(ch for ch in phone if ch.isdigit())[-9:]


@router.post(
    "/orders/lookup",
    response={200: OrderLookupOut, 404: ErrorOut},
    throttle=[AnonRateThrottle("20/h")],
)
def lookup_order(request, payload: OrderLookupIn):
    """Найти заказ по номеру и телефону — для страницы «Отследить заказ»."""
    number = payload.number.strip().upper()
    if not number.startswith("MS-"):
        number = f"MS-{number}"
    order = Order.objects.filter(number=number).first()
    if order is None or phone_digits(order.phone) != phone_digits(payload.phone):
        # Одинаковый ответ: нельзя узнать, существует ли заказ с таким номером
        return Status(404, {"detail": "Order not found."})
    return Status(200, {"token": order.token})


# Объявлен после /orders/lookup: иначе «lookup» совпал бы с {token}
@router.get("/orders/{token}", response=OrderOut)
def get_order(request, token: str):
    """Статус заказа для покупателя — по секретной ссылке, без регистрации."""
    return get_object_or_404(
        Order.objects.select_related("delivery_method").prefetch_related("items"), token=token
    )
