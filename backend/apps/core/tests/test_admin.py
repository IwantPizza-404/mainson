"""Все страницы админки открываются: список, добавление, редактирование."""

import pytest
from django.contrib import admin
from django.urls import reverse

from apps.catalog.tests.factories import ProductFactory, SpecOptionFactory, WatchSpecsFactory

pytestmark = pytest.mark.django_db

MODEL_ADMINS = list(admin.site._registry.items())


@pytest.fixture
def superuser(django_user_model):
    return django_user_model.objects.create_superuser("admin", "admin@maison.uz", "pass")


@pytest.fixture
def staff_client(client, superuser):
    client.force_login(superuser)
    return client


def test_index(staff_client):
    assert staff_client.get(reverse("admin:index")).status_code == 200


@pytest.mark.parametrize(
    ("model", "model_admin"),
    MODEL_ADMINS,
    ids=[model._meta.label_lower for model, _ in MODEL_ADMINS],
)
def test_changelist_and_add(staff_client, superuser, rf, model, model_admin):
    WatchSpecsFactory(case_material=SpecOptionFactory())
    base = f"admin:{model._meta.app_label}_{model._meta.model_name}"
    request = rf.get("/")
    request.user = superuser
    # Некоторые модели (например, курсы валют) нельзя добавлять вручную
    expected_add_status = 200 if model_admin.has_add_permission(request) else 403

    # Одиночные записи (настройки сайта) перенаправляют со списка на форму — идём по редиректу
    assert staff_client.get(reverse(f"{base}_changelist"), follow=True).status_code == 200
    assert staff_client.get(reverse(f"{base}_add")).status_code == expected_add_status


def test_product_change_has_translation_fields(staff_client):
    product = ProductFactory()

    response = staff_client.get(reverse("admin:catalog_product_change", args=[product.pk]))

    assert response.status_code == 200
    html = response.content.decode()
    assert all(f'name="name_{lang}"' in html for lang in ("en", "ru", "uz"))
