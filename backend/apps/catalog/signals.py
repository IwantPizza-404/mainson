from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import ProductImage
from .tasks import process_product_image


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
