from django.core.cache import cache
from django.db import connection
from ninja import Router, Schema

router = Router(tags=["system"])


class HealthOut(Schema):
    status: str
    database: bool
    cache: bool


@router.get("/health", response=HealthOut, auth=None)
def health(request):
    """Проверка доступности сервиса и зависимостей (для балансировщика и мониторинга)."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_ok = True
    except Exception:
        db_ok = False

    try:
        cache.set("health", "ok", 5)
        cache_ok = cache.get("health") == "ok"
    except Exception:
        cache_ok = False

    return {
        "status": "ok" if db_ok and cache_ok else "degraded",
        "database": db_ok,
        "cache": cache_ok,
    }
