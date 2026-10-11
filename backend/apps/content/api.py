from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from ninja import Router

from apps.catalog.api import brands_with_counts
from apps.catalog.models import Product
from apps.core.responsive import responsive_image

from .models import FaqItem, HomeSection, HomeSectionItem, Page, SiteSettings
from .schemas import (
    FaqItemOut,
    HomeSectionOut,
    PageLinkOut,
    PageOut,
    SitemapOut,
    SiteSettingsOut,
)
from .services import brands_with_products, section_products

router = Router(tags=["content"])

Kind = HomeSection.Kind


@router.get("/home", response=list[HomeSectionOut])
def home(request):
    sections = HomeSection.objects.filter(is_active=True).prefetch_related(
        Prefetch("items", queryset=HomeSectionItem.objects.order_by("position", "id"))
    )
    brands = None
    result = []
    for section in sections:
        if section.kind == Kind.BRANDS and brands is None:
            brands = list(brands_with_products())
        result.append(
            {
                "id": section.pk,
                "kind": section.kind,
                "title": section.title,
                "subtitle": section.subtitle,
                "button_label": section.button_label,
                "link": section.link,
                "image": responsive_image(section, "image", request),
                "image_mobile": responsive_image(section, "image_mobile", request),
                "items": list(section.items.all()),
                "products": list(section_products(section))
                if section.kind == Kind.PRODUCTS
                else [],
                "brands": brands if section.kind == Kind.BRANDS else [],
            }
        )
    # Пустые карусели и бренды не показываем
    return [
        s
        for s in result
        if not (s["kind"] == Kind.PRODUCTS and not s["products"])
        and not (s["kind"] == Kind.BRANDS and not s["brands"])
    ]


@router.get("/settings", response=SiteSettingsOut)
def site_settings(request):
    return SiteSettings.load()


@router.get("/pages", response=list[PageLinkOut])
def list_pages(request):
    """Опубликованные страницы — для подвала и sitemap."""
    return Page.objects.filter(is_published=True)


@router.get("/pages/{slug}", response=PageOut)
def get_page(request, slug: str):
    return get_object_or_404(Page, slug=slug, is_published=True)


@router.get("/faq", response=list[FaqItemOut])
def list_faq(request):
    return FaqItem.objects.filter(is_published=True)


@router.get("/sitemap", response=SitemapOut)
def sitemap(request):
    """Адреса для sitemap.xml витрины."""
    return {
        "products": Product.objects.published().values("slug", "updated_at"),
        "brands": brands_with_counts().values("slug"),
        "pages": Page.objects.filter(is_published=True).values("slug", "updated_at"),
    }
