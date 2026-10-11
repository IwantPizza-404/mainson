"""Способы доставки по умолчанию. Дальше редактируются в админке."""

from django.db import migrations

METHODS = [
    # code, scope, price, en, ru, uz (название, описание)
    (
        "pickup-tashkent", "pickup", "0",
        ("Pickup in Tashkent", "Free, by appointment"),
        ("Самовывоз в Ташкенте", "Бесплатно, по договорённости"),
        ("Toshkentda olib ketish", "Bepul, kelishuv asosida"),
    ),
    (
        "courier-tashkent", "domestic", None,
        ("Courier in Tashkent", "Cost confirmed by the manager"),
        ("Курьер по Ташкенту", "Стоимость уточнит менеджер"),
        ("Toshkent bo‘ylab kuryer", "Narxini menejer aniqlaydi"),
    ),
    (
        "bts-uzbekistan", "domestic", None,
        ("BTS delivery across Uzbekistan", "Cost confirmed by the manager"),
        ("BTS по Узбекистану", "Стоимость уточнит менеджер"),
        ("BTS orqali O‘zbekiston bo‘ylab", "Narxini menejer aniqlaydi"),
    ),
    (
        "bts-international", "international", None,
        ("BTS international delivery", "Cost and timing confirmed by the manager"),
        ("BTS — доставка в другие страны", "Стоимость и сроки уточнит менеджер"),
        ("BTS — xalqaro yetkazib berish", "Narx va muddatni menejer aniqlaydi"),
    ),
]


def create(apps, schema_editor):
    DeliveryMethod = apps.get_model("orders", "DeliveryMethod")
    for position, (code, scope, price, en, ru, uz) in enumerate(METHODS):
        DeliveryMethod.objects.update_or_create(
            code=code,
            defaults={
                "scope": scope,
                "price": price,
                "position": position,
                "name": en[0], "name_en": en[0], "name_ru": ru[0], "name_uz": uz[0],
                "description": en[1], "description_en": en[1],
                "description_ru": ru[1], "description_uz": uz[1],
            },
        )


def remove(apps, schema_editor):
    apps.get_model("orders", "DeliveryMethod").objects.filter(
        code__in=[m[0] for m in METHODS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("orders", "0001_initial")]
    operations = [migrations.RunPython(create, remove)]
