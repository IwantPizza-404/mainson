"""Отслеживание изменений товаров и заявок → уведомления покупателям (после коммита, в фоне)."""

from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.catalog.models import Product

from .models import WatchRequest
from .tasks import notify_product_events, notify_watch_request

Availability = Product.Availability


@receiver(pre_save, sender=Product)
def remember_product_state(sender, instance: Product, **kwargs) -> None:
    previous = (
        Product.objects.filter(pk=instance.pk)
        .values("availability", "is_published", "price")
        .first()
        if instance.pk
        else None
    )
    instance._previous_state = previous  # type: ignore[attr-defined]


@receiver(post_save, sender=Product)
def detect_product_events(sender, instance: Product, created: bool, **kwargs) -> None:
    previous = getattr(instance, "_previous_state", None)
    if not instance.is_published:
        return
    events = []
    was_published = bool(previous and previous["is_published"])
    if not was_published:
        events.append("published")
    if instance.is_purchasable and (
        not was_published or (previous and previous["availability"] == Availability.SOLD_OUT)
    ):
        events.append("back_in_stock")
    if previous and instance.price < previous["price"]:
        events.append("price_dropped")
    if events:
        pk = instance.pk
        transaction.on_commit(lambda: notify_product_events.delay(pk, events))


@receiver(pre_save, sender=WatchRequest)
def remember_request_state(sender, instance: WatchRequest, **kwargs) -> None:
    previous = (
        WatchRequest.objects.filter(pk=instance.pk).values("status", "reply").first()
        if instance.pk
        else None
    )
    instance._previous_state = previous  # type: ignore[attr-defined]


@receiver(post_save, sender=WatchRequest)
def detect_request_events(sender, instance: WatchRequest, created: bool, **kwargs) -> None:
    previous = getattr(instance, "_previous_state", None)
    changed = previous and (
        previous["status"] != instance.status or previous["reply"] != instance.reply
    )
    if created or changed:
        pk = instance.pk
        transaction.on_commit(lambda: notify_watch_request.delay(pk, created))
