from celery import shared_task

from .services import RatesFetchError, update_rates


@shared_task(autoretry_for=(RatesFetchError,), retry_backoff=60, max_retries=5)
def update_exchange_rates() -> list[str]:
    return update_rates()
