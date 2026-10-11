from .base import *  # noqa: F403
from .base import AWS_STORAGE_BUCKET_NAME, env

DEBUG = False

# Публичный адрес сайта: https://maison.uz
PUBLIC_URL = env("PUBLIC_URL").rstrip("/")
BACKEND_URL = PUBLIC_URL
SITE_URL = PUBLIC_URL

# HTTPS завершается на Caddy. Редирект на https в Django не включаем: витрина при SSR ходит
# к бэкенду по внутренней сети (http://backend:8000) и получала бы редирект вместо данных.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
# HSTS выставляет Caddy для всего домена

# Один прокси (Caddy) перед бэкендом: реальный IP покупателя — из X-Forwarded-For.
# Без этого лимит заказов считал бы всех покупателей одним IP прокси.
NINJA_NUM_PROXIES = 1

# Медиа на локальном диске сервера раздаёт Caddy. Адрес абсолютный: иначе при SSR ссылки
# на фото строились бы от внутреннего имени http://backend:8000
if not AWS_STORAGE_BUCKET_NAME:
    MEDIA_URL = f"{PUBLIC_URL}/media/"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="Maison <noreply@maison.uz>")

# Мониторинг ошибок — если задан SENTRY_DSN
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=env("SENTRY_ENVIRONMENT", default="production"),
        traces_sample_rate=0.1,
        send_default_pii=False,  # без персональных данных покупателей
    )
