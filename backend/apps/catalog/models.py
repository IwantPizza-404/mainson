from decimal import Decimal
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.db.models.fields.files import FieldFile
from django.utils.translation import gettext_lazy as _

from apps.core.images import (
    ALLOWED_EXTENSIONS,
    PRODUCT_VARIANTS,
    open_normalized,
    render_variant,
    validate_image_size,
    variant_filename,
)
from apps.core.models import TimeStampedModel

if TYPE_CHECKING:
    from django_stubs_ext import StrOrPromise


class Brand(TimeStampedModel):
    name = models.CharField(_("name"), max_length=120, unique=True)
    slug = models.SlugField(_("slug"), max_length=140, unique=True)
    logo = models.ImageField(_("logo"), upload_to="brands/", blank=True)
    country = models.CharField(_("country"), max_length=80, blank=True)
    description = models.TextField(_("description"), blank=True)
    search_aliases = models.CharField(
        _("search aliases"),
        max_length=255,
        blank=True,
        help_text=_("Other spellings for search, comma-separated: ролекс, ролех"),
    )
    is_active = models.BooleanField(_("active"), default=True)
    position = models.PositiveIntegerField(_("position"), default=0, db_index=True)

    class Meta:
        verbose_name = _("brand")
        verbose_name_plural = _("brands")
        ordering = ["position", "name"]

    def __str__(self) -> str:
        return self.name


class Category(TimeStampedModel):
    """Категория товаров: часы, ремешки, аксессуары. Один уровень вложенности."""

    name = models.CharField(_("name"), max_length=120)
    slug = models.SlugField(_("slug"), max_length=140, unique=True)
    parent = models.ForeignKey(
        "self",
        verbose_name=_("parent"),
        on_delete=models.PROTECT,
        related_name="children",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(_("active"), default=True)
    position = models.PositiveIntegerField(_("position"), default=0, db_index=True)

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["position", "name"]

    def __str__(self) -> str:
        return f"{self.parent} / {self.name}" if self.parent_id else self.name

    def clean(self) -> None:
        if self.parent is not None and (self.parent_id == self.pk or self.parent.parent_id):
            raise ValidationError({"parent": _("Only one level of nesting is allowed.")})


class SpecOption(models.Model):
    """Значение из справочника характеристик (материал корпуса, цвет циферблата и т.д.).

    Справочник редактируется в админке, значения переводятся на все языки сайта
    и используются как фильтры каталога.
    """

    class Kind(models.TextChoices):
        CASE_MATERIAL = "case_material", _("Case material")
        STRAP_MATERIAL = "strap_material", _("Strap material")
        DIAL_COLOR = "dial_color", _("Dial color")
        GLASS = "glass", _("Glass")
        COMPLICATION = "complication", _("Complication")

    kind = models.CharField(_("kind"), max_length=32, choices=Kind.choices, db_index=True)
    name = models.CharField(_("name"), max_length=120)
    slug = models.SlugField(_("slug"), max_length=140)
    position = models.PositiveIntegerField(_("position"), default=0)

    class Meta:
        verbose_name = _("specification option")
        verbose_name_plural = _("specification options")
        ordering = ["kind", "position", "name"]
        constraints = [
            models.UniqueConstraint(fields=["kind", "slug"], name="uniq_specoption_kind_slug"),
        ]

    def __str__(self) -> str:
        return self.name


class ProductQuerySet(models.QuerySet["Product"]):
    def published(self) -> "ProductQuerySet":
        return self.filter(is_published=True, brand__is_active=True, category__is_active=True)


class Product(TimeStampedModel):
    class Condition(models.TextChoices):
        NEW = "new", _("New")
        PRE_OWNED = "pre_owned", _("Pre-owned")

    class Availability(models.TextChoices):
        IN_STOCK = "in_stock", _("In stock")
        ON_ORDER = "on_order", _("On order")
        SOLD_OUT = "sold_out", _("Sold out")

    class Gender(models.TextChoices):
        MEN = "men", _("Men")
        WOMEN = "women", _("Women")
        UNISEX = "unisex", _("Unisex")

    category = models.ForeignKey(
        Category, verbose_name=_("category"), on_delete=models.PROTECT, related_name="products"
    )
    brand = models.ForeignKey(
        Brand, verbose_name=_("brand"), on_delete=models.PROTECT, related_name="products"
    )
    name = models.CharField(_("name"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=220, unique=True)
    reference = models.CharField(
        _("reference"), max_length=80, blank=True, db_index=True, help_text=_("Model reference")
    )
    description = models.TextField(_("description"), blank=True)

    # Цены хранятся только в базовой валюте (settings.BASE_CURRENCY).
    price = models.DecimalField(
        _("price, USD"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    compare_at_price = models.DecimalField(
        _("old price, USD"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Crossed-out price shown for discounted items."),
    )

    condition = models.CharField(
        _("condition"), max_length=16, choices=Condition.choices, default=Condition.NEW
    )
    gender = models.CharField(
        _("gender"), max_length=16, choices=Gender.choices, default=Gender.UNISEX
    )

    availability = models.CharField(
        _("availability"),
        max_length=16,
        choices=Availability.choices,
        default=Availability.IN_STOCK,
        db_index=True,
    )
    stock_quantity = models.PositiveIntegerField(_("stock quantity"), default=0)
    lead_time_days = models.PositiveSmallIntegerField(
        _("lead time, days"),
        null=True,
        blank=True,
        help_text=_("Delivery time for items on order."),
    )

    is_published = models.BooleanField(_("published"), default=False, db_index=True)
    is_featured = models.BooleanField(_("featured"), default=False)

    seo_title = models.CharField(_("SEO title"), max_length=160, blank=True)
    seo_description = models.CharField(_("SEO description"), max_length=320, blank=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_published", "availability", "-created_at"]),
            models.Index(fields=["brand", "is_published"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(compare_at_price__isnull=True)
                | models.Q(compare_at_price__gt=models.F("price")),
                name="product_compare_at_price_gt_price",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.brand} {self.name}" if self.brand_id else self.name

    def clean(self) -> None:
        errors: dict[str, StrOrPromise] = {}
        if (
            self.compare_at_price is not None
            and self.price is not None
            and self.compare_at_price <= self.price
        ):
            errors["compare_at_price"] = _("Old price must be greater than the price.")
        if self.availability == self.Availability.IN_STOCK and self.stock_quantity == 0:
            errors["stock_quantity"] = _("Set the quantity for an item in stock.")
        if self.availability == self.Availability.ON_ORDER and not self.lead_time_days:
            errors["lead_time_days"] = _("Set the lead time for an item on order.")
        if errors:
            raise ValidationError(errors)

    @property
    def is_purchasable(self) -> bool:
        return self.availability != self.Availability.SOLD_OUT


def limit_to(kind: SpecOption.Kind) -> dict[str, str]:
    return {"kind": kind}


class WatchSpecs(models.Model):
    """Характеристики часов. Есть только у товаров-часов, поэтому вынесены из Product."""

    class Movement(models.TextChoices):
        AUTOMATIC = "automatic", _("Automatic")
        MANUAL = "manual", _("Manual winding")
        QUARTZ = "quartz", _("Quartz")
        SOLAR = "solar", _("Solar")

    product = models.OneToOneField(
        Product, verbose_name=_("product"), on_delete=models.CASCADE, related_name="watch_specs"
    )

    movement = models.CharField(_("movement"), max_length=16, choices=Movement.choices, blank=True)
    caliber = models.CharField(_("caliber"), max_length=80, blank=True)
    power_reserve_hours = models.PositiveSmallIntegerField(
        _("power reserve, hours"), null=True, blank=True
    )

    case_material = models.ForeignKey(
        SpecOption,
        verbose_name=_("case material"),
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to=limit_to(SpecOption.Kind.CASE_MATERIAL),
        null=True,
        blank=True,
    )
    case_diameter_mm = models.DecimalField(
        _("case diameter, mm"), max_digits=4, decimal_places=1, null=True, blank=True
    )
    case_thickness_mm = models.DecimalField(
        _("case thickness, mm"), max_digits=4, decimal_places=1, null=True, blank=True
    )
    glass = models.ForeignKey(
        SpecOption,
        verbose_name=_("glass"),
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to=limit_to(SpecOption.Kind.GLASS),
        null=True,
        blank=True,
    )
    water_resistance_m = models.PositiveSmallIntegerField(
        _("water resistance, m"), null=True, blank=True
    )

    dial_color = models.ForeignKey(
        SpecOption,
        verbose_name=_("dial color"),
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to=limit_to(SpecOption.Kind.DIAL_COLOR),
        null=True,
        blank=True,
    )
    strap_material = models.ForeignKey(
        SpecOption,
        verbose_name=_("strap / bracelet material"),
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to=limit_to(SpecOption.Kind.STRAP_MATERIAL),
        null=True,
        blank=True,
    )
    complications = models.ManyToManyField(
        SpecOption,
        verbose_name=_("complications"),
        related_name="+",
        limit_choices_to=limit_to(SpecOption.Kind.COMPLICATION),
        blank=True,
    )

    year = models.PositiveSmallIntegerField(_("year"), null=True, blank=True)
    has_box = models.BooleanField(_("original box"), default=False)
    has_papers = models.BooleanField(_("papers / warranty card"), default=False)
    # Серийный номер — только для внутреннего учёта (б/у экземпляры), в API не отдаётся.
    serial_number = models.CharField(_("serial number"), max_length=80, blank=True)

    class Meta:
        verbose_name = _("watch specifications")
        verbose_name_plural = _("watch specifications")

    def __str__(self) -> str:
        return str(self.product)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, verbose_name=_("product"), on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(
        _("image"),
        upload_to="products/%Y/%m/",
        validators=[FileExtensionValidator(ALLOWED_EXTENSIONS), validate_image_size],
        width_field="width",
        height_field="height",
    )
    alt = models.CharField(_("alt text"), max_length=200, blank=True)
    position = models.PositiveIntegerField(_("position"), default=0, db_index=True)

    width = models.PositiveIntegerField(editable=False, null=True)
    height = models.PositiveIntegerField(editable=False, null=True)

    # WebP-варианты для витрины — создаются фоновой задачей после загрузки
    thumb = models.ImageField(upload_to="products/variants/%Y/%m/", editable=False, blank=True)
    medium = models.ImageField(upload_to="products/variants/%Y/%m/", editable=False, blank=True)
    large = models.ImageField(upload_to="products/variants/%Y/%m/", editable=False, blank=True)
    # Имя оригинала, для которого построены варианты: при замене фото они пересоздаются
    processed_for = models.CharField(max_length=255, editable=False, blank=True)

    class Meta:
        verbose_name = _("image")
        verbose_name_plural = _("images")
        ordering = ["position", "id"]

    def __str__(self) -> str:
        return f"{self.product} #{self.position}"

    @property
    def needs_processing(self) -> bool:
        return bool(self.image) and self.processed_for != self.image.name

    def variant_files(self) -> list[FieldFile]:
        return [getattr(self, v.name) for v in PRODUCT_VARIANTS if getattr(self, v.name)]

    def stored_file_names(self, *, include_original: bool = True) -> list[str]:
        files = [self.image, *self.variant_files()] if include_original else self.variant_files()
        return [f.name for f in files if f.name]

    def process(self) -> None:
        """Строит WebP-варианты из оригинала и удаляет устаревшие."""
        original_name = self.image.name
        if not original_name:
            return
        stale = self.stored_file_names(include_original=False)
        source = open_normalized(self.image)
        for variant in PRODUCT_VARIANTS:
            getattr(self, variant.name).save(
                variant_filename(original_name, variant),
                render_variant(source, variant),
                save=False,
            )
        self.processed_for = original_name
        self.save(update_fields=[v.name for v in PRODUCT_VARIANTS] + ["processed_for"])
        storage = self.image.storage
        for name in stale:
            storage.delete(name)
