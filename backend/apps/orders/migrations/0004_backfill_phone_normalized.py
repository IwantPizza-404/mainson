from django.db import migrations


def normalize(phone: str) -> str:
    # Копия apps.accounts.models.normalize_phone: миграции не импортируют код приложения
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) == 9:
        digits = "998" + digits
    return f"+{digits}" if digits else ""


def backfill(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    for order in Order.objects.filter(phone_normalized=""):
        order.phone_normalized = normalize(order.phone)
        order.save(update_fields=["phone_normalized"])


class Migration(migrations.Migration):
    dependencies = [("orders", "0003_customer_tracking_warranty")]
    operations = [migrations.RunPython(backfill, migrations.RunPython.noop)]
