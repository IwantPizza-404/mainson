from decimal import Decimal
from typing import Annotated

from django.db.models import Q
from ninja import Field, FilterLookup, FilterSchema, Schema

from .models import Product, ProductImage, SpecOption, WatchSpecs


def absolute_url(context: dict | None, url: str) -> str:
    request = context.get("request") if context else None
    return request.build_absolute_uri(url) if request else url


# --- Справочники -------------------------------------------------------------


class BrandRef(Schema):
    name: str
    slug: str


class BrandOut(Schema):
    name: str
    slug: str
    country: str
    description: str
    logo: str | None
    # Число опубликованных товаров (аннотация brands_with_counts)
    product_count: int = 0

    @staticmethod
    def resolve_logo(obj, context) -> str | None:
        return absolute_url(context, obj.logo.url) if obj.logo else None


class CategoryOut(Schema):
    name: str
    slug: str
    parent: str | None = Field(None, alias="parent.slug")


class SpecOptionOut(Schema):
    name: str
    slug: str


class ChoiceOut(Schema):
    value: str
    label: str


# --- Товар -------------------------------------------------------------------


class ImageOut(Schema):
    """Фото товара. thumb/medium/large — WebP 400/800/1600 px для srcset.

    Пока варианты не построены (фоновая задача ещё не отработала), во всех полях — оригинал.
    """

    url: str
    thumb: str
    medium: str
    large: str
    width: int | None
    height: int | None
    alt: str

    @staticmethod
    def resolve_url(obj: ProductImage, context) -> str:
        return absolute_url(context, obj.image.url)

    @staticmethod
    def _variant(obj: ProductImage, name: str, context) -> str:
        field = getattr(obj, name)
        return absolute_url(context, (field or obj.image).url)

    @staticmethod
    def resolve_thumb(obj: ProductImage, context) -> str:
        return ImageOut._variant(obj, "thumb", context)

    @staticmethod
    def resolve_medium(obj: ProductImage, context) -> str:
        return ImageOut._variant(obj, "medium", context)

    @staticmethod
    def resolve_large(obj: ProductImage, context) -> str:
        return ImageOut._variant(obj, "large", context)


class WatchSpecsOut(Schema):
    movement: ChoiceOut | None
    caliber: str
    power_reserve_hours: int | None
    case_material: SpecOptionOut | None
    case_diameter_mm: Decimal | None
    case_thickness_mm: Decimal | None
    glass: SpecOptionOut | None
    water_resistance_m: int | None
    dial_color: SpecOptionOut | None
    strap_material: SpecOptionOut | None
    complications: list[SpecOptionOut]
    year: int | None
    has_box: bool
    has_papers: bool

    @staticmethod
    def resolve_movement(obj: WatchSpecs) -> dict | None:
        if not obj.movement:
            return None
        return {"value": obj.movement, "label": obj.get_movement_display()}

    @staticmethod
    def resolve_complications(obj: WatchSpecs) -> list[SpecOption]:
        return list(obj.complications.all())


class ProductListOut(Schema):
    slug: str
    name: str
    brand: BrandRef
    reference: str
    price: Decimal
    compare_at_price: Decimal | None
    condition: ChoiceOut
    availability: ChoiceOut
    lead_time_days: int | None
    image: ImageOut | None

    @staticmethod
    def resolve_condition(obj: Product) -> dict:
        return {"value": obj.condition, "label": obj.get_condition_display()}

    @staticmethod
    def resolve_availability(obj: Product) -> dict:
        return {"value": obj.availability, "label": obj.get_availability_display()}

    @staticmethod
    def resolve_image(obj: Product) -> ProductImage | None:
        # images предзагружены через prefetch_related — не делаем лишний запрос
        images = obj.images.all()
        return images[0] if images else None


class ProductDetailOut(ProductListOut):
    description: str
    category: CategoryOut
    gender: ChoiceOut
    images: list[ImageOut]
    watch_specs: WatchSpecsOut | None
    seo_title: str
    seo_description: str

    @staticmethod
    def resolve_gender(obj: Product) -> dict:
        return {"value": obj.gender, "label": obj.get_gender_display()}

    @staticmethod
    def resolve_images(obj: Product) -> list[ProductImage]:
        return list(obj.images.all())

    @staticmethod
    def resolve_watch_specs(obj: Product) -> WatchSpecs | None:
        return getattr(obj, "watch_specs", None)


# --- Фильтры каталога ----------------------------------------------------------


class ProductFilters(FilterSchema):
    q: str | None = None
    # Конкретные товары по slug — для гостевого избранного
    slug: list[str] = []
    brand: list[str] = []
    category: str | None = None
    condition: list[Product.Condition] = []
    availability: list[Product.Availability] = []
    gender: list[Product.Gender] = []
    movement: list[WatchSpecs.Movement] = []
    case_material: list[str] = []
    dial_color: list[str] = []
    strap_material: list[str] = []
    price_min: Annotated[Decimal | None, FilterLookup(q="price__gte")] = None
    price_max: Annotated[Decimal | None, FilterLookup(q="price__lte")] = None
    diameter_min: Annotated[
        Decimal | None, FilterLookup(q="watch_specs__case_diameter_mm__gte")
    ] = None
    diameter_max: Annotated[
        Decimal | None, FilterLookup(q="watch_specs__case_diameter_mm__lte")
    ] = None

    def filter_q(self, value: str | None) -> Q:
        if not value:
            return Q()
        return (
            Q(name__icontains=value)
            | Q(reference__icontains=value)
            | Q(brand__name__icontains=value)
        )

    def filter_slug(self, value: list[str]) -> Q:
        return Q(slug__in=value[:100]) if value else Q()

    def filter_brand(self, value: list[str]) -> Q:
        return Q(brand__slug__in=value) if value else Q()

    def filter_category(self, value: str | None) -> Q:
        # Категория включает товары подкатегорий
        if not value:
            return Q()
        return Q(category__slug=value) | Q(category__parent__slug=value)

    def filter_condition(self, value: list[str]) -> Q:
        return Q(condition__in=value) if value else Q()

    def filter_availability(self, value: list[str]) -> Q:
        return Q(availability__in=value) if value else Q()

    def filter_gender(self, value: list[str]) -> Q:
        return Q(gender__in=value) if value else Q()

    def filter_movement(self, value: list[str]) -> Q:
        return Q(watch_specs__movement__in=value) if value else Q()

    def filter_case_material(self, value: list[str]) -> Q:
        return Q(watch_specs__case_material__slug__in=value) if value else Q()

    def filter_dial_color(self, value: list[str]) -> Q:
        return Q(watch_specs__dial_color__slug__in=value) if value else Q()

    def filter_strap_material(self, value: list[str]) -> Q:
        return Q(watch_specs__strap_material__slug__in=value) if value else Q()


class PriceRange(Schema):
    min: Decimal | None
    max: Decimal | None


class FiltersOut(Schema):
    """Варианты для панели фильтров витрины."""

    brands: list[BrandRef]
    categories: list[CategoryOut]
    conditions: list[ChoiceOut]
    availability: list[ChoiceOut]
    genders: list[ChoiceOut]
    movements: list[ChoiceOut]
    case_materials: list[SpecOptionOut]
    dial_colors: list[SpecOptionOut]
    strap_materials: list[SpecOptionOut]
    price: PriceRange
