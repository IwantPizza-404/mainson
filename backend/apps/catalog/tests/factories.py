from decimal import Decimal

import factory

from apps.catalog.models import Brand, Category, Product, SpecOption, WatchSpecs


class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brand

    name = factory.Sequence(lambda n: f"Brand {n}")
    slug = factory.Sequence(lambda n: f"brand-{n}")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")


class SpecOptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpecOption

    kind = SpecOption.Kind.CASE_MATERIAL
    name = factory.Sequence(lambda n: f"Option {n}")
    slug = factory.Sequence(lambda n: f"option-{n}")


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    brand = factory.SubFactory(BrandFactory)
    category = factory.SubFactory(CategoryFactory)
    name = factory.Sequence(lambda n: f"Watch {n}")
    slug = factory.Sequence(lambda n: f"watch-{n}")
    price = Decimal("1000.00")
    stock_quantity = 1
    is_published = True


class WatchSpecsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WatchSpecs

    product = factory.SubFactory(ProductFactory)
    movement = WatchSpecs.Movement.AUTOMATIC
