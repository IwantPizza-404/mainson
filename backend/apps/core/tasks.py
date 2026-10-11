from celery import shared_task
from django.apps import apps


@shared_task(autoretry_for=(OSError,), retry_backoff=10, max_retries=3)
def process_responsive_images(model_label: str, pk: int) -> None:
    model = apps.get_model(model_label)
    obj = model.objects.filter(pk=pk).first()
    if obj is not None:
        obj.process_images()
