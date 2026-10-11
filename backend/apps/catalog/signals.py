from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Brand, Category, Product, ProductImage
from .tasks import process_product_image, sync_search_index


@receiver(post_save, sender=ProductImage)
def schedule_image_processing(sender, instance: ProductImage, **kwargs) -> None:
    if instance.needs_processing:
        # После коммита — чтобы воркер точно увидел запись в базе
        transaction.on_commit(lambda: process_product_image.delay(instance.pk))


@receiver(post_delete, sender=ProductImage)
def delete_image_files(sender, instance: ProductImage, **kwargs) -> None:
    names = instance.stored_file_names()
    storage = instance.image.storage

    def delete_files() -> None:
        for name in names:
            storage.delete(name)

    transaction.on_commit(delete_files)


def schedule_search_sync(ids: list[int]) -> None:
    if ids:
        transaction.on_commit(lambda: sync_search_index.delay(ids))


@receiver([post_save, post_delete], sender=Product)
def sync_product(sender, instance: Product, **kwargs) -> None:
    schedule_search_sync([instance.pk])


@receiver(post_save, sender=Brand)
@receiver(post_save, sender=Category)
def sync_related_products(sender, instance, **kwargs) -> None:
    # Название бренда или активность категории влияют на поиск всех её товаров
    schedule_search_sync(list(instance.products.values_list("pk", flat=True)))
