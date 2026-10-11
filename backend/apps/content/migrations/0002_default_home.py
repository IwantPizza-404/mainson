"""Главная по умолчанию — чтобы сайт выглядел законченным до загрузки баннеров.

Тексты блока преимуществ — черновик, заказчик правит их в админке.
"""

from django.db import migrations


def tr(en: str, ru: str, uz: str, field: str) -> dict:
    return {field: en, f"{field}_en": en, f"{field}_ru": ru, f"{field}_uz": uz}


SECTIONS = [
    {
        "kind": "hero",
        "items": [
            {
                **tr("Luxury watches", "Элитные часы", "Hashamatli soatlar", "title"),
                **tr(
                    "Authentic timepieces with worldwide delivery",
                    "Оригинальные часы с доставкой по всему миру",
                    "Butun dunyo bo‘ylab yetkazib beriladigan original soatlar",
                    "text",
                ),
                **tr("Explore the collection", "Смотреть коллекцию", "Kolleksiyani ko‘rish", "button_label"),
                "link": "/watches",
            }
        ],
    },
    {"kind": "trust", "items": [
        {"icon": "shield-check", **tr("100% authentic", "100% оригинал", "100% original", "title"),
         **tr("Every watch is checked before sale", "Каждые часы проверяются перед продажей",
              "Har bir soat sotuvdan oldin tekshiriladi", "text")},
        {"icon": "globe", **tr("Worldwide delivery", "Доставка по миру", "Butun dunyo bo‘ylab", "title"),
         **tr("Across Uzbekistan and abroad with BTS", "По Узбекистану и за рубеж через BTS",
              "O‘zbekiston bo‘ylab va xorijga BTS orqali", "text")},
        {"icon": "headset", **tr("Personal manager", "Личный менеджер", "Shaxsiy menejer", "title"),
         **tr("Help with choice and payment", "Поможет с выбором и оплатой",
              "Tanlash va to‘lovda yordam beradi", "text")},
        {"icon": "badge-check", **tr("Box & papers", "Комплект и документы", "Quti va hujjatlar", "title"),
         **tr("Full set listed for every watch", "Комплектация указана у каждых часов",
              "Har bir soat uchun to‘plam ko‘rsatilgan", "text")},
    ]},
    {"kind": "products", "product_source": "new", "limit": 8,
     **tr("New arrivals", "Новинки", "Yangi kelganlar", "title")},
    {"kind": "tiles", "items": [
        {**tr("For him", "Для него", "Erkaklar uchun", "title"), "link": "/watches?gender=men",
         **tr("Shop now", "Смотреть", "Ko‘rish", "button_label")},
        {**tr("For her", "Для неё", "Ayollar uchun", "title"), "link": "/watches?gender=women",
         **tr("Shop now", "Смотреть", "Ko‘rish", "button_label")},
    ]},
    {"kind": "brands", **tr("Our brands", "Наши бренды", "Brendlarimiz", "title")},
    {"kind": "products", "product_source": "pre_owned", "limit": 8,
     **tr("Pre-owned", "С историей", "Ishlatilgan", "title"),
     **tr("Inspected watches with history", "Проверенные часы с историей",
          "Tekshirilgan, tarixga ega soatlar", "subtitle")},
]


def create(apps, schema_editor):
    HomeSection = apps.get_model("content", "HomeSection")
    HomeSectionItem = apps.get_model("content", "HomeSectionItem")
    SiteSettings = apps.get_model("content", "SiteSettings")
    SiteSettings.objects.get_or_create(pk=1)
    if HomeSection.objects.exists():
        return
    for position, data in enumerate(SECTIONS):
        data = dict(data)
        items = data.pop("items", [])
        section = HomeSection.objects.create(position=position, **data)
        for item_position, item in enumerate(items):
            HomeSectionItem.objects.create(section=section, position=item_position, **item)


class Migration(migrations.Migration):
    dependencies = [("content", "0001_initial")]
    operations = [migrations.RunPython(create, migrations.RunPython.noop)]
