"""Черновики информационных страниц и FAQ (не опубликованы).

Заполнены только известными фактами (BTS, оплата через менеджера). Юридические тексты
(гарантия, возврат, политика, соглашение) должен предоставить заказчик.
"""

from django.db import migrations

TODO = {
    "en": "<p>Text will be provided by the store.</p>",
    "ru": "<p>Текст предоставит магазин.</p>",
    "uz": "<p>Matnni do‘kon taqdim etadi.</p>",
}

PAGES = [
    ("about", "about", ("About Maison", "О Maison", "Maison haqida"), TODO),
    (
        "delivery",
        "customers",
        ("Delivery and payment", "Доставка и оплата", "Yetkazib berish va to‘lov"),
        {
            "en": "<h2>Delivery</h2><ul><li>Pickup in Tashkent — free, by appointment.</li>"
            "<li>Courier in Tashkent and BTS delivery across Uzbekistan.</li>"
            "<li>International delivery with BTS — cost and timing confirmed by the manager.</li></ul>"
            "<h2>Payment</h2><p>After you place an order, our manager contacts you to confirm "
            "the details and arrange payment.</p>",
            "ru": "<h2>Доставка</h2><ul><li>Самовывоз в Ташкенте — бесплатно, по договорённости.</li>"
            "<li>Курьер по Ташкенту и BTS по Узбекистану.</li>"
            "<li>Доставка в другие страны через BTS — стоимость и сроки уточнит менеджер.</li></ul>"
            "<h2>Оплата</h2><p>После оформления заказа менеджер свяжется с вами, подтвердит детали "
            "и согласует оплату.</p>",
            "uz": "<h2>Yetkazib berish</h2><ul><li>Toshkentda olib ketish — bepul, kelishuv asosida.</li>"
            "<li>Toshkent bo‘ylab kuryer va O‘zbekiston bo‘ylab BTS.</li>"
            "<li>Boshqa mamlakatlarga BTS orqali — narx va muddatni menejer aniqlaydi.</li></ul>"
            "<h2>To‘lov</h2><p>Buyurtma berganingizdan so‘ng menejer siz bilan bog‘lanib, "
            "tafsilotlarni tasdiqlaydi va to‘lovni kelishadi.</p>",
        },
    ),
    ("warranty", "customers", ("Warranty and authenticity", "Гарантия и подлинность", "Kafolat va originallik"), TODO),
    ("returns", "customers", ("Returns and exchange", "Возврат и обмен", "Qaytarish va almashtirish"), TODO),
    ("privacy", "legal", ("Privacy policy", "Политика конфиденциальности", "Maxfiylik siyosati"), TODO),
    ("terms", "legal", ("Terms of use", "Пользовательское соглашение", "Foydalanish shartlari"), TODO),
]

FAQ = [
    (
        ("Are the watches authentic?", "Часы оригинальные?", "Soatlar originalmi?"),
        ("Yes. Every watch is checked before sale.", "Да. Каждые часы проверяются перед продажей.",
         "Ha. Har bir soat sotuvdan oldin tekshiriladi."),
    ),
    (
        ("How do I pay for my order?", "Как оплатить заказ?", "Buyurtmani qanday to‘layman?"),
        ("After you place an order, our manager contacts you and arranges payment.",
         "После оформления заказа менеджер свяжется с вами и согласует оплату.",
         "Buyurtma berganingizdan so‘ng menejer siz bilan bog‘lanib, to‘lovni kelishadi."),
    ),
    (
        ("Can I order a watch that is not in stock?", "Можно ли заказать часы, которых нет в наличии?",
         "Mavjud bo‘lmagan soatni buyurtma qilsa bo‘ladimi?"),
        ("Yes. Watches marked “On order” are delivered within the time shown on the product page.",
         "Да. Часы с пометкой «Под заказ» привозятся в срок, указанный на странице товара.",
         "Ha. «Buyurtma asosida» belgisi bor soatlar mahsulot sahifasida ko‘rsatilgan muddatda yetkaziladi."),
    ),
    (
        ("Do you deliver abroad?", "Вы доставляете в другие страны?", "Boshqa mamlakatlarga yetkazib berasizmi?"),
        ("Yes, with BTS. The manager confirms the cost and timing.",
         "Да, через BTS. Стоимость и сроки уточнит менеджер.",
         "Ha, BTS orqali. Narx va muddatni menejer aniqlaydi."),
    ),
]


def create(apps, schema_editor):
    Page = apps.get_model("content", "Page")
    FaqItem = apps.get_model("content", "FaqItem")
    for position, (slug, group, (en, ru, uz), content) in enumerate(PAGES):
        Page.objects.get_or_create(
            slug=slug,
            defaults={
                "footer_group": group,
                "position": position,
                "is_published": False,
                "title": en, "title_en": en, "title_ru": ru, "title_uz": uz,
                "content": content["en"], "content_en": content["en"],
                "content_ru": content["ru"], "content_uz": content["uz"],
            },
        )
    if not FaqItem.objects.exists():
        for position, ((qen, qru, quz), (aen, aru, auz)) in enumerate(FAQ):
            FaqItem.objects.create(
                position=position,
                is_published=False,
                question=qen, question_en=qen, question_ru=qru, question_uz=quz,
                answer=f"<p>{aen}</p>", answer_en=f"<p>{aen}</p>",
                answer_ru=f"<p>{aru}</p>", answer_uz=f"<p>{auz}</p>",
            )


class Migration(migrations.Migration):
    dependencies = [("content", "0003_pages_faq")]
    operations = [migrations.RunPython(create, migrations.RunPython.noop)]
