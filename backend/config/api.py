"""Корневой роутер публичного API. Каждый модуль подключает свой Router сюда."""

from ninja import NinjaAPI

from apps.catalog.api import router as catalog_router
from apps.core.api import router as core_router

api = NinjaAPI(
    title="Maison API",
    version="1.0.0",
    urls_namespace="api",
)

api.add_router("/", core_router)
api.add_router("/catalog", catalog_router)
