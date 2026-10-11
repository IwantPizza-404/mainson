"""Все страницы админки открываются: список, добавление, редактирование."""

import pytest
from django.contrib import admin
from django.urls import reverse

from apps.catalog.tests.factories import ProductFactory, SpecOptionFactory, WatchSpecsFactory

pytestmark = pytest.mark.django_db

MODEL_ADMINS = [model._meta for model in admin.site._registry]


@pytest.fixture
def staff_client(client, django_user_model):
    user = django_user_model.objects.create_superuser("admin", "admin@maison.uz", "pass")
    client.force_login(user)
    return client


def test_index(staff_client):
    assert staff_client.get(reverse("admin:index")).status_code == 200


@pytest.mark.parametrize("opts", MODEL_ADMINS, ids=lambda o: o.label_lower)
def test_changelist_and_add(staff_client, opts):
    WatchSpecsFactory(case_material=SpecOptionFactory())
    base = f"admin:{opts.app_label}_{opts.model_name}"

    assert staff_client.get(reverse(f"{base}_changelist")).status_code == 200
    assert staff_client.get(reverse(f"{base}_add")).status_code == 200


def test_product_change_has_translation_fields(staff_client):
    product = ProductFactory()

    response = staff_client.get(reverse("admin:catalog_product_change", args=[product.pk]))

    assert response.status_code == 200
    html = response.content.decode()
    assert all(f'name="name_{lang}"' in html for lang in ("en", "ru", "uz"))
