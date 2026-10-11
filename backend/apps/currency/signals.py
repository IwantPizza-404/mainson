from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import ExchangeRate
from .services import RATES_CACHE_KEY


@receiver([post_save, post_delete], sender=ExchangeRate)
def reset_rates_cache(**kwargs) -> None:
    # Правка курса в админке сразу видна на витрине
    cache.delete(RATES_CACHE_KEY)
