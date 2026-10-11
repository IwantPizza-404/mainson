from modeltranslation.translator import TranslationOptions, register

from .models import Brand, Category, Product, ProductImage, SpecOption


@register(Brand)
class BrandTranslationOptions(TranslationOptions):
    fields = ("description",)


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(SpecOption)
class SpecOptionTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ("name", "description", "seo_title", "seo_description")


@register(ProductImage)
class ProductImageTranslationOptions(TranslationOptions):
    fields = ("alt",)
