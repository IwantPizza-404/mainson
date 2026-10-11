from ninja import Schema

from apps.catalog.schemas import BrandOut, ProductListOut
from apps.core.responsive import responsive_image


class ResponsiveImageOut(Schema):
    url: str
    srcset: str | None
    width: int | None
    height: int | None


class SectionItemOut(Schema):
    title: str
    text: str
    button_label: str
    link: str
    icon: str
    image: ResponsiveImageOut | None
    image_mobile: ResponsiveImageOut | None

    @staticmethod
    def resolve_image(obj, context) -> dict | None:
        return responsive_image(obj, "image", context["request"])

    @staticmethod
    def resolve_image_mobile(obj, context) -> dict | None:
        return responsive_image(obj, "image_mobile", context["request"])


class HomeSectionOut(Schema):
    """Секция главной. Поля, не относящиеся к типу секции, пустые."""

    id: int
    kind: str
    title: str
    subtitle: str
    button_label: str
    link: str
    image: ResponsiveImageOut | None
    image_mobile: ResponsiveImageOut | None
    items: list[SectionItemOut]
    products: list[ProductListOut]
    brands: list[BrandOut]


class SiteSettingsOut(Schema):
    phone: str
    email: str
    telegram_username: str
    whatsapp_number: str
    instagram_url: str
    telegram_channel_url: str
    facebook_url: str
    youtube_url: str
    address: str
    working_hours: str
    announcement: str
    announcement_link: str
