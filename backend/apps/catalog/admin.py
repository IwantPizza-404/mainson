from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.contrib.filters.admin import (
    ChoicesDropdownFilter,
    RangeNumericFilter,
    RelatedDropdownFilter,
)
from unfold.decorators import action, display

from .models import Brand, Category, Product, ProductImage, SpecOption, WatchSpecs


@admin.register(Brand)
class BrandAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ("name", "country", "products_count", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "search_aliases")
    prepopulated_fields = {"slug": ("name",)}
    ordering_field = "position"
    hide_ordering_field = True

    @display(description=_("products"))
    def products_count(self, obj: Brand) -> int:
        return obj.products.count()


@admin.register(Category)
class CategoryAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ("__str__", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name_en",)}
    ordering_field = "position"
    hide_ordering_field = True


@admin.register(SpecOption)
class SpecOptionAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ("name", "kind")
    list_filter = (("kind", ChoicesDropdownFilter),)
    list_filter_submit = True
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name_en",)}
    ordering_field = "position"
    hide_ordering_field = True


class WatchSpecsInline(StackedInline):
    model = WatchSpecs
    can_delete = False
    autocomplete_fields = ("case_material", "glass", "dial_color", "strap_material")
    filter_horizontal = ("complications",)
    fieldsets = (
        (_("Movement"), {"fields": (("movement", "caliber", "power_reserve_hours"),)}),
        (
            _("Case"),
            {
                "fields": (
                    ("case_material", "case_diameter_mm", "case_thickness_mm"),
                    ("glass", "water_resistance_m"),
                )
            },
        ),
        (_("Dial & strap"), {"fields": (("dial_color", "strap_material"), "complications")}),
        (
            _("Set & provenance"),
            {"fields": (("year", "has_box", "has_papers"), "serial_number")},
        ),
    )


class ProductImageInline(TabularInline, TranslationTabularInline):
    model = ProductImage
    extra = 0
    fields = ("preview", "image", "alt", "position")
    readonly_fields = ("preview",)
    ordering_field = "position"
    hide_ordering_field = True

    @display(description=_("preview"))
    def preview(self, obj: ProductImage) -> str:
        if not obj.image:
            return "—"
        return format_html('<img src="{}" style="height:64px">', (obj.thumb or obj.image).url)


@admin.register(Product)
class ProductAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = (
        "thumbnail",
        "name",
        "brand",
        "reference",
        "price",
        "availability_badge",
        "stock_quantity",
        "is_published",
    )
    list_display_links = ("thumbnail", "name")
    list_filter = (
        ("brand", RelatedDropdownFilter),
        ("category", RelatedDropdownFilter),
        ("availability", ChoicesDropdownFilter),
        ("condition", ChoicesDropdownFilter),
        ("gender", ChoicesDropdownFilter),
        ("price", RangeNumericFilter),
        "is_published",
        "is_featured",
    )
    list_filter_submit = True
    list_per_page = 50
    search_fields = ("name", "reference", "brand__name", "watch_specs__serial_number")
    autocomplete_fields = ("brand", "category")
    prepopulated_fields = {"slug": ("name_en",)}
    list_select_related = ("brand", "category")
    inlines = (WatchSpecsInline, ProductImageInline)
    actions = ("publish", "unpublish")
    fieldsets = (
        (None, {"fields": (("brand", "category"), "name", "slug", "reference", "description")}),
        (_("Price"), {"fields": (("price", "compare_at_price"),)}),
        (
            _("Availability"),
            {"fields": (("availability", "stock_quantity", "lead_time_days"),)},
        ),
        (_("Attributes"), {"fields": (("condition", "gender"),)}),
        (_("Publishing"), {"fields": (("is_published", "is_featured"),)}),
        (
            _("SEO"),
            {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Product]:
        return super().get_queryset(request).prefetch_related("images")

    @display(description="")
    def thumbnail(self, obj: Product) -> str:
        images = list(obj.images.all())
        if not images:
            return "—"
        return format_html(
            '<img src="{}" style="height:40px;width:40px;object-fit:cover">',
            (images[0].thumb or images[0].image).url,
        )

    @display(
        description=_("availability"),
        label={
            Product.Availability.IN_STOCK: "success",
            Product.Availability.ON_ORDER: "warning",
            Product.Availability.SOLD_OUT: "danger",
        },
    )
    def availability_badge(self, obj: Product) -> tuple[str, str]:
        return obj.availability, obj.get_availability_display()

    @action(description=_("Publish selected"))
    def publish(self, request: HttpRequest, queryset: QuerySet[Product]) -> None:
        updated = queryset.update(is_published=True)
        self.message_user(request, _("Published: %d") % updated, messages.SUCCESS)

    @action(description=_("Unpublish selected"))
    def unpublish(self, request: HttpRequest, queryset: QuerySet[Product]) -> None:
        updated = queryset.update(is_published=False)
        self.message_user(request, _("Unpublished: %d") % updated, messages.SUCCESS)
