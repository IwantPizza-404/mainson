from django.contrib import admin
from django.db import models
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TabbedTranslationAdmin, TranslationStackedInline
from unfold.admin import ModelAdmin, StackedInline
from unfold.contrib.forms.widgets import WysiwygWidget

from .models import FaqItem, HomeSection, HomeSectionItem, Page, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin, TabbedTranslationAdmin):
    fieldsets = (
        (_("Contacts"), {"fields": (("phone", "email"), "address", "working_hours")}),
        (_("Messengers"), {"fields": (("telegram_username", "whatsapp_number"),)}),
        (
            _("Social networks"),
            {
                "fields": (
                    ("instagram_url", "telegram_channel_url"),
                    ("facebook_url", "youtube_url"),
                )
            },
        ),
        (_("Announcement bar"), {"fields": ("announcement", "announcement_link")}),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # Ссылки без схемы (instagram.com/…) дополняем https://
        if isinstance(db_field, models.URLField):
            kwargs["assume_scheme"] = "https"
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def changelist_view(self, request, extra_context=None):
        # Одна запись — сразу открываем её
        obj = SiteSettings.load()
        return HttpResponseRedirect(reverse("admin:content_sitesettings_change", args=[obj.pk]))


class HomeSectionItemInline(StackedInline, TranslationStackedInline):
    model = HomeSectionItem
    extra = 0
    ordering_field = "position"
    hide_ordering_field = True
    fields = (
        ("title", "icon"),
        "text",
        ("button_label", "link"),
        ("image", "image_mobile"),
        "position",
    )


@admin.register(HomeSection)
class HomeSectionAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ("__str__", "kind", "is_active")
    list_filter = ("kind", "is_active")
    ordering_field = "position"
    hide_ordering_field = True
    inlines = (HomeSectionItemInline,)
    autocomplete_fields = ("brand", "products")
    fieldsets = (
        (None, {"fields": (("kind", "is_active"), "title", "subtitle")}),
        (
            _("Products"),
            {"fields": (("product_source", "limit"), "brand", "products")},
        ),
        (_("Banner"), {"fields": (("image", "image_mobile"), ("button_label", "link"))}),
    )
    # Поля показываются только для подходящего типа секции (Alpine.js в Unfold)
    conditional_fields = {
        "product_source": "kind == 'products'",
        "limit": "kind == 'products'",
        "brand": "kind == 'products' && product_source == 'brand'",
        "products": "kind == 'products' && product_source == 'manual'",
        "image": "kind == 'banner'",
        "image_mobile": "kind == 'banner'",
        "button_label": "kind == 'banner'",
        "link": "kind == 'banner'",
    }


@admin.register(Page)
class PageAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ("title", "slug", "footer_group", "is_published", "updated_at")
    list_filter = ("is_published", "footer_group")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title_en",)}
    ordering_field = "position"
    hide_ordering_field = True
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget}}
    fieldsets = (
        (None, {"fields": ("title", "slug", "content")}),
        (_("Publishing"), {"fields": (("is_published", "footer_group"), "seo_description")}),
    )


@admin.register(FaqItem)
class FaqItemAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ("question", "is_published")
    list_filter = ("is_published",)
    search_fields = ("question",)
    ordering_field = "position"
    hide_ordering_field = True
    formfield_overrides = {models.TextField: {"widget": WysiwygWidget}}
    fields = ("question", "answer", "is_published")
