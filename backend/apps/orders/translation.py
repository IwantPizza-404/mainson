from modeltranslation.translator import TranslationOptions, register

from .models import DeliveryMethod


@register(DeliveryMethod)
class DeliveryMethodTranslationOptions(TranslationOptions):
    fields = ("name", "description")
