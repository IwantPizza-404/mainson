from modeltranslation.translator import TranslationOptions, register

from .models import FaqItem, HomeSection, HomeSectionItem, Page, SiteSettings


@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    fields = ("address", "working_hours", "announcement")


@register(HomeSection)
class HomeSectionTranslationOptions(TranslationOptions):
    fields = ("title", "subtitle", "button_label")


@register(HomeSectionItem)
class HomeSectionItemTranslationOptions(TranslationOptions):
    fields = ("title", "text", "button_label")


@register(Page)
class PageTranslationOptions(TranslationOptions):
    fields = ("title", "content", "seo_description")


@register(FaqItem)
class FaqItemTranslationOptions(TranslationOptions):
    fields = ("question", "answer")
