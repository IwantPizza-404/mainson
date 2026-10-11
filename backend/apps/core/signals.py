from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .responsive import ResponsiveImagesMixin
from .tasks import process_responsive_images


@receiver(post_save)
def schedule_responsive_images(sender, instance, **kwargs) -> None:
    if isinstance(instance, ResponsiveImagesMixin) and instance.images_to_process():
        label, pk = instance._meta.label, instance.pk
        transaction.on_commit(lambda: process_responsive_images.delay(label, pk))


@receiver(post_delete)
def delete_responsive_files(sender, instance, **kwargs) -> None:
    if not isinstance(instance, ResponsiveImagesMixin):
        return
    files = instance.all_stored_files()
    storage = next(iter(getattr(instance, n) for n in instance.RESPONSIVE_IMAGES)).storage

    def delete() -> None:
        for name in files:
            storage.delete(name)

    transaction.on_commit(delete)
