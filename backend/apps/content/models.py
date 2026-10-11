from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.html import clean_html
from apps.core.images import ALLOWED_EXTENSIONS, validate_image_size
from apps.core.responsive import BANNER_VARIANTS, TILE_VARIANTS, ResponsiveImagesMixin

IMAGE_VALIDATORS = [FileExtensionValidator(ALLOWED_EXTENSIONS), validate_image_size]


def clean_translated_html(obj: models.Model, field: str) -> None:
    """HTML из редактора очищается на всех языках: на сайт попадает только безопасная разметка."""
    for code, _name in settings.LANGUAGES:
        name = f"{field}_{code}"
        setattr(obj, name, clean_html(getattr(obj, name, "") or ""))


def validate_link(value: str) -> None:
    """Ссылка — путь на сайте (/watches?brand=rolex) или полный адрес https://…"""
    if value and not value.startswith(("/", "https://", "http://")):
        raise ValidationError(_("Use a path starting with “/” or a full https:// address."))


class SiteSettings(models.Model):
    """Настройки сайта — одна запись: контакты, соцсети, строка объявления."""

    phone = models.CharField(_("phone"), max_length=32, blank=True)
    email = models.EmailField(_("email"), blank=True)
    telegram_username = models.CharField(
        _("Telegram username"), max_length=64, blank=True, help_text=_("Without @")
    )
    whatsapp_number = models.CharField(
        _("WhatsApp number"), max_length=20, blank=True, help_text=_("Digits only: 998901234567")
    )
    instagram_url = models.URLField(_("Instagram"), blank=True)
    telegram_channel_url = models.URLField(_("Telegram channel"), blank=True)
    facebook_url = models.URLField(_("Facebook"), blank=True)
    youtube_url = models.URLField(_("YouTube"), blank=True)
    address = models.CharField(_("address"), max_length=255, blank=True)
    working_hours = models.CharField(_("working hours"), max_length=120, blank=True)
    announcement = models.CharField(
        _("announcement"),
        max_length=200,
        blank=True,
        help_text=_("Thin bar above the header, e.g. a promotion. Empty — hidden."),
    )
    announcement_link = models.CharField(
        _("announcement link"), max_length=255, blank=True, validators=[validate_link]
    )

    class Meta:
        verbose_name = _("site settings")
        verbose_name_plural = _("site settings")

    def __str__(self) -> str:
        return str(_("Site settings"))

    def save(self, *args, **kwargs) -> None:
        self.pk = 1
        self.whatsapp_number = "".join(ch for ch in self.whatsapp_number if ch.isdigit())
        self.telegram_username = self.telegram_username.lstrip("@").strip()
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "SiteSettings":
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj


class HomeSection(ResponsiveImagesMixin, models.Model):
    """Секция главной страницы. Порядок и состав редактируются в админке."""

    class Kind(models.TextChoices):
        HERO = "hero", _("Hero slider")
        PRODUCTS = "products", _("Product carousel")
        BRANDS = "brands", _("Brand logos")
        TILES = "tiles", _("Tiles (e.g. For him / For her)")
        BANNER = "banner", _("Wide banner")
        TRUST = "trust", _("Benefits bar")

    class ProductSource(models.TextChoices):
        NEW = "new", _("New arrivals")
        FEATURED = "featured", _("Featured")
        SALE = "sale", _("Discounted")
        PRE_OWNED = "pre_owned", _("Pre-owned")
        BRAND = "brand", _("Brand")
        MANUAL = "manual", _("Selected manually")

    RESPONSIVE_IMAGES = {"image": BANNER_VARIANTS, "image_mobile": TILE_VARIANTS}

    kind = models.CharField(_("type"), max_length=16, choices=Kind.choices)
    title = models.CharField(_("title"), max_length=150, blank=True)
    subtitle = models.CharField(_("subtitle"), max_length=255, blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    position = models.PositiveIntegerField(_("position"), default=0, db_index=True)

    # Карусель товаров
    product_source = models.CharField(
        _("products"), max_length=16, choices=ProductSource.choices, blank=True
    )
    brand = models.ForeignKey(
        "catalog.Brand", verbose_name=_("brand"), on_delete=models.CASCADE, null=True, blank=True
    )
    products = models.ManyToManyField(
        "catalog.Product", verbose_name=_("selected products"), blank=True, related_name="+"
    )
    limit = models.PositiveSmallIntegerField(
        _("number of products"), default=8, validators=[MinValueValidator(1), MaxValueValidator(24)]
    )

    # Широкий баннер
    image = models.ImageField(
        _("image"), upload_to="content/%Y/%m/", blank=True, validators=IMAGE_VALIDATORS
    )
    image_variants = models.JSONField(default=dict, editable=False)
    image_mobile = models.ImageField(
        _("image for phones"),
        upload_to="content/%Y/%m/",
        blank=True,
        validators=IMAGE_VALIDATORS,
        help_text=_("Optional vertical version for phones."),
    )
    image_mobile_variants = models.JSONField(default=dict, editable=False)
    button_label = models.CharField(_("button label"), max_length=60, blank=True)
    link = models.CharField(_("link"), max_length=255, blank=True, validators=[validate_link])

    class Meta:
        verbose_name = _("home page section")
        verbose_name_plural = _("home page")
        ordering = ["position", "id"]

    def __str__(self) -> str:
        return self.title or self.get_kind_display()

    def clean(self) -> None:
        if self.kind == self.Kind.PRODUCTS:
            if not self.product_source:
                raise ValidationError({"product_source": _("Choose which products to show.")})
            if self.product_source == self.ProductSource.BRAND and not self.brand_id:
                raise ValidationError({"brand": _("Choose a brand.")})
        if self.kind == self.Kind.BANNER and not self.image:
            raise ValidationError({"image": _("A banner needs an image.")})


class HomeSectionItem(ResponsiveImagesMixin, models.Model):
    """Элемент секции: слайд, плитка или пункт блока преимуществ."""

    class Icon(models.TextChoices):
        SHIELD = "shield-check", _("Shield (authenticity)")
        TRUCK = "truck", _("Truck (delivery)")
        GLOBE = "globe", _("Globe (worldwide)")
        GEM = "gem", _("Gem (premium)")
        HEADSET = "headset", _("Headset (support)")
        BADGE = "badge-check", _("Badge (warranty)")
        WALLET = "wallet", _("Wallet (payment)")
        CLOCK = "clock", _("Clock")

    RESPONSIVE_IMAGES = {"image": BANNER_VARIANTS, "image_mobile": TILE_VARIANTS}

    section = models.ForeignKey(HomeSection, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(_("title"), max_length=150, blank=True)
    text = models.CharField(_("text"), max_length=255, blank=True)
    button_label = models.CharField(_("button label"), max_length=60, blank=True)
    link = models.CharField(_("link"), max_length=255, blank=True, validators=[validate_link])
    icon = models.CharField(_("icon"), max_length=32, choices=Icon.choices, blank=True)
    image = models.ImageField(
        _("image"), upload_to="content/%Y/%m/", blank=True, validators=IMAGE_VALIDATORS
    )
    image_variants = models.JSONField(default=dict, editable=False)
    image_mobile = models.ImageField(
        _("image for phones"), upload_to="content/%Y/%m/", blank=True, validators=IMAGE_VALIDATORS
    )
    image_mobile_variants = models.JSONField(default=dict, editable=False)
    position = models.PositiveIntegerField(_("position"), default=0, db_index=True)

    class Meta:
        verbose_name = _("item")
        verbose_name_plural = _("items")
        ordering = ["position", "id"]

    def __str__(self) -> str:
        return self.title or f"#{self.position}"


class Page(models.Model):
    """Информационная страница: о нас, доставка и оплата, гарантия, возврат, политика и т.д."""

    class FooterGroup(models.TextChoices):
        CUSTOMERS = "customers", _("For customers")
        ABOUT = "about", _("About")
        LEGAL = "legal", _("Legal")

    slug = models.SlugField(
        _("address"), max_length=80, unique=True, help_text=_("maison.uz/<address>")
    )
    title = models.CharField(_("title"), max_length=150)
    content = models.TextField(_("content"), blank=True)
    footer_group = models.CharField(
        _("footer column"), max_length=16, choices=FooterGroup.choices, blank=True
    )
    is_published = models.BooleanField(_("published"), default=False)
    position = models.PositiveIntegerField(_("position"), default=0, db_index=True)
    seo_description = models.CharField(_("SEO description"), max_length=320, blank=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("page")
        verbose_name_plural = _("pages")
        ordering = ["position", "id"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        clean_translated_html(self, "content")
        super().save(*args, **kwargs)


class FaqItem(models.Model):
    question = models.CharField(_("question"), max_length=255)
    answer = models.TextField(_("answer"))
    is_published = models.BooleanField(_("published"), default=True)
    position = models.PositiveIntegerField(_("position"), default=0, db_index=True)

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("FAQ")
        ordering = ["position", "id"]

    def __str__(self) -> str:
        return self.question

    def save(self, *args, **kwargs) -> None:
        clean_translated_html(self, "answer")
        super().save(*args, **kwargs)
