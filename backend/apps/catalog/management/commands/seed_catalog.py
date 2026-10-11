"""Начальные справочники каталога (en / ru / uz) и, опционально, демо-товары.

    python manage.py seed_catalog          # только справочники
    python manage.py seed_catalog --demo   # + демо-бренды и товары для разработки

Команда идемпотентна: повторный запуск не создаёт дубликатов.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import Brand, Category, Product, SpecOption, WatchSpecs

Kind = SpecOption.Kind

CATEGORIES = [
    ("watches", "Watches", "Часы", "Soatlar"),
    ("straps", "Straps", "Ремешки", "Tasmalar"),
    ("accessories", "Accessories", "Аксессуары", "Aksessuarlar"),
]

# Переводы на узбекский нужно согласовать с заказчиком.
SPEC_OPTIONS = {
    Kind.CASE_MATERIAL: [
        ("stainless-steel", "Stainless steel", "Нержавеющая сталь", "Zanglamas po‘lat"),
        ("yellow-gold", "Yellow gold", "Жёлтое золото", "Sariq oltin"),
        ("rose-gold", "Rose gold", "Розовое золото", "Pushti oltin"),
        ("white-gold", "White gold", "Белое золото", "Oq oltin"),
        ("platinum", "Platinum", "Платина", "Platina"),
        ("titanium", "Titanium", "Титан", "Titan"),
        ("ceramic", "Ceramic", "Керамика", "Keramika"),
        ("two-tone", "Steel & gold", "Сталь и золото", "Po‘lat va oltin"),
    ],
    Kind.GLASS: [
        ("sapphire", "Sapphire crystal", "Сапфировое стекло", "Sapfir oyna"),
        ("mineral", "Mineral glass", "Минеральное стекло", "Mineral oyna"),
        ("acrylic", "Acrylic", "Акрил", "Akril"),
    ],
    Kind.DIAL_COLOR: [
        ("black", "Black", "Чёрный", "Qora"),
        ("white", "White", "Белый", "Oq"),
        ("silver", "Silver", "Серебристый", "Kumushrang"),
        ("blue", "Blue", "Синий", "Ko‘k"),
        ("green", "Green", "Зелёный", "Yashil"),
        ("grey", "Grey", "Серый", "Kulrang"),
        ("champagne", "Champagne", "Шампань", "Shampan"),
        ("brown", "Brown", "Коричневый", "Jigarrang"),
    ],
    Kind.STRAP_MATERIAL: [
        ("steel-bracelet", "Steel bracelet", "Стальной браслет", "Po‘lat bilaguzuk"),
        ("gold-bracelet", "Gold bracelet", "Золотой браслет", "Oltin bilaguzuk"),
        ("leather", "Leather strap", "Кожаный ремешок", "Charm tasma"),
        ("rubber", "Rubber strap", "Каучуковый ремешок", "Kauchuk tasma"),
        ("textile", "Textile strap", "Текстильный ремешок", "Mato tasma"),
    ],
    Kind.COMPLICATION: [
        ("date", "Date", "Дата", "Sana"),
        ("chronograph", "Chronograph", "Хронограф", "Xronograf"),
        ("gmt", "GMT", "GMT", "GMT"),
        ("moon-phase", "Moon phase", "Фаза луны", "Oy fazasi"),
        ("perpetual-calendar", "Perpetual calendar", "Вечный календарь", "Abadiy taqvim"),
        ("tourbillon", "Tourbillon", "Турбийон", "Turbiyon"),
        (
            "power-reserve-indicator",
            "Power reserve indicator",
            "Индикатор запаса хода",
            "Quvvat zaxirasi ko‘rsatkichi",
        ),
    ],
}

DEMO_BRANDS = [
    ("rolex", "Rolex", "Switzerland"),
    ("omega", "Omega", "Switzerland"),
    ("cartier", "Cartier", "France"),
    ("tudor", "Tudor", "Switzerland"),
]

# slug, brand, name, reference, price, old price, availability, condition, gender,
# movement, diameter, case, dial, strap, complications
DEMO_PRODUCTS = [
    (
        "submariner-date",
        "rolex",
        "Submariner Date",
        "126610LN",
        "14500",
        None,
        "in_stock",
        "new",
        "men",
        "automatic",
        "41",
        "stainless-steel",
        "black",
        "steel-bracelet",
        ["date"],
    ),
    (
        "datejust-36",
        "rolex",
        "Datejust 36",
        "126234",
        "11200",
        None,
        "on_order",
        "new",
        "unisex",
        "automatic",
        "36",
        "stainless-steel",
        "blue",
        "steel-bracelet",
        ["date"],
    ),
    (
        "gmt-master-ii",
        "rolex",
        "GMT-Master II",
        "126710BLRO",
        "19800",
        None,
        "in_stock",
        "pre_owned",
        "men",
        "automatic",
        "40",
        "stainless-steel",
        "black",
        "steel-bracelet",
        ["date", "gmt"],
    ),
    (
        "speedmaster-moonwatch",
        "omega",
        "Speedmaster Moonwatch",
        "310.30.42.50.01.001",
        "7600",
        None,
        "in_stock",
        "new",
        "men",
        "manual",
        "42",
        "stainless-steel",
        "black",
        "steel-bracelet",
        ["chronograph"],
    ),
    (
        "seamaster-aqua-terra",
        "omega",
        "Seamaster Aqua Terra",
        "220.10.41.21.03.004",
        "6100",
        "6900",
        "in_stock",
        "new",
        "men",
        "automatic",
        "41",
        "stainless-steel",
        "blue",
        "steel-bracelet",
        ["date"],
    ),
    (
        "santos-de-cartier",
        "cartier",
        "Santos de Cartier",
        "WSSA0029",
        "8100",
        None,
        "on_order",
        "new",
        "unisex",
        "automatic",
        "39.8",
        "stainless-steel",
        "silver",
        "steel-bracelet",
        [],
    ),
    (
        "tank-must",
        "cartier",
        "Tank Must",
        "WSTA0042",
        "3250",
        None,
        "in_stock",
        "new",
        "women",
        "quartz",
        "29.5",
        "stainless-steel",
        "silver",
        "leather",
        [],
    ),
    (
        "black-bay-58",
        "tudor",
        "Black Bay 58",
        "M79030N",
        "4300",
        None,
        "sold_out",
        "new",
        "men",
        "automatic",
        "39",
        "stainless-steel",
        "black",
        "steel-bracelet",
        [],
    ),
]


def translated(slug: str, en: str, ru: str, uz: str) -> dict:
    return {"slug": slug, "name_en": en, "name_ru": ru, "name_uz": uz}


class Command(BaseCommand):
    help = "Создаёт справочники каталога и (с --demo) демо-товары."

    def add_arguments(self, parser):
        parser.add_argument("--demo", action="store_true", help="Добавить демо-бренды и товары")

    @transaction.atomic
    def handle(self, *args, demo: bool = False, **options):
        for position, row in enumerate(CATEGORIES):
            data = translated(*row)
            Category.objects.update_or_create(
                slug=data.pop("slug"), defaults={**data, "position": position}
            )

        for kind, rows in SPEC_OPTIONS.items():
            for position, row in enumerate(rows):
                data = translated(*row)
                SpecOption.objects.update_or_create(
                    kind=kind, slug=data.pop("slug"), defaults={**data, "position": position}
                )

        self.stdout.write(self.style.SUCCESS("Справочники созданы."))

        if demo:
            self._seed_demo()
            self.stdout.write(self.style.SUCCESS(f"Демо-товары: {len(DEMO_PRODUCTS)}."))

    def _seed_demo(self) -> None:
        watches = Category.objects.get(slug="watches")
        brands = {}
        for position, (slug, name, country) in enumerate(DEMO_BRANDS):
            brands[slug], _ = Brand.objects.update_or_create(
                slug=slug, defaults={"name": name, "country": country, "position": position}
            )

        def option(kind: Kind, slug: str) -> SpecOption:
            return SpecOption.objects.get(kind=kind, slug=slug)

        for (
            slug,
            brand,
            name,
            reference,
            price,
            old_price,
            availability,
            condition,
            gender,
            movement,
            diameter,
            case,
            dial,
            strap,
            complications,
        ) in DEMO_PRODUCTS:
            product, _ = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    "brand": brands[brand],
                    "category": watches,
                    "name_en": name,
                    "reference": reference,
                    "price": Decimal(price),
                    "compare_at_price": Decimal(old_price) if old_price else None,
                    "availability": availability,
                    "stock_quantity": 1 if availability == "in_stock" else 0,
                    "lead_time_days": 14 if availability == "on_order" else None,
                    "condition": condition,
                    "gender": gender,
                    "is_published": True,
                },
            )
            specs, _ = WatchSpecs.objects.update_or_create(
                product=product,
                defaults={
                    "movement": movement,
                    "case_diameter_mm": Decimal(diameter),
                    "case_material": option(Kind.CASE_MATERIAL, case),
                    "dial_color": option(Kind.DIAL_COLOR, dial),
                    "strap_material": option(Kind.STRAP_MATERIAL, strap),
                    "glass": option(Kind.GLASS, "sapphire"),
                    "water_resistance_m": 100,
                    "has_box": True,
                    "has_papers": condition == "new",
                },
            )
            specs.complications.set([option(Kind.COMPLICATION, c) for c in complications])
