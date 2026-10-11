from celery import shared_task

from .models import ProductImage


@shared_task(autoretry_for=(OSError,), retry_backoff=10, max_retries=3)
def process_product_image(image_id: int) -> None:
    image = ProductImage.objects.filter(pk=image_id).first()
    if image and image.needs_processing:
        image.process()
