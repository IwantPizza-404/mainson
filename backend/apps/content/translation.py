from modeltranslation.translator import TranslationOptions, register

from .models import HomeSection, HomeSectionItem, SiteSettings


@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    fields = ("address", "working_hours", "announcement")


@register(HomeSection)
class HomeSectionTranslationOptions(TranslationOptions):
    fields = ("title", "subtitle", "button_label")


@register(HomeSectionItem)
class HomeSectionItemTranslationOptions(TranslationOptions):
    fields = ("title", "text", "button_label")
