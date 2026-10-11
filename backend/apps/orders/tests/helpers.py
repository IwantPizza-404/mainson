"""Общие данные для тестов заказов."""


def order_payload(**overrides) -> dict:
    payload = {
        "items": [{"slug": "watch", "quantity": 1}],
        "customer_name": "Aziz",
        "phone": "+998 90 123 45 67",
        "contact_method": "telegram",
        "country": "UZ",
        "city": "Tashkent",
        "delivery_method": "pickup-tashkent",
        "currency": "UZS",
    }
    payload.update(overrides)
    return payload
