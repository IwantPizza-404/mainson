# Maison — maison.uz

Интернет-магазин часов. Продажи в Узбекистане и по всему миру, сайт на трёх языках: en / uz / ru.

## Стек

| Слой | Технологии |
|---|---|
| Витрина | Nuxt 4 (Vue 3, TypeScript, SSR), Pinia, Tailwind CSS 4, @nuxtjs/i18n |
| Бэкенд | Django 5.2 LTS, Django Ninja (REST + OpenAPI), Celery |
| Админка | Django Admin + Unfold |
| Данные | PostgreSQL 17, Redis, Meilisearch |
| Медиа | Локально — диск, prod — S3-совместимое хранилище (Cloudflare R2) |

## Структура

```
backend/     Django: config/ (настройки, API, Celery), apps/ (модули предметной области)
frontend/    Nuxt: app/ (страницы, компоненты, сторы), i18n/locales/ (переводы)
infra/       docker-compose для локальной инфраструктуры
```

Каждый модуль бэкенда (каталог, заказы, оплата, доставка, контент) — отдельное Django-приложение в `backend/apps/`
со своим `api.py` (Ninja Router), который подключается в `config/api.py`.

## Быстрый старт

Требуется: Docker, [uv](https://docs.astral.sh/uv/), Node 24 (`nvm use`), pnpm (`corepack enable pnpm`).

```bash
make up          # Postgres (порт 5433), Redis, Meilisearch, Mailpit
make setup       # зависимости + .env из .env.example
make migrate
make seed          # справочники каталога + 8 демо-часов
make rates         # курсы валют из ЦБ Узбекистана
make superuser
make backend     # http://localhost:8000/admin, API-документация: http://localhost:8000/api/v1/docs
make frontend    # http://localhost:3000
make worker      # фоновые задачи и расписание (обновление курсов 2 раза в день)
```

Письма в dev ловит Mailpit: http://localhost:8025

## Ключевые решения

- **Базовая валюта — USD.** Цены хранятся только в USD. UZS / EUR / RUB — пересчёт для отображения по курсу ЦБ Узбекистана (обновляется Celery в 9:30 и 15:30). В админке можно задать ручной курс и наценку. Заказ фиксирует курс на момент оформления.
- **Языки:** контент переводится в админке (django-modeltranslation), фолбэк — английский. URL витрины: `/`, `/uz/…`, `/ru/…`.
- **Оплата:** на старте — через менеджера (Telegram / WhatsApp); онлайн-провайдеры (Payme, Click, международный эквайринг) подключаются как отдельные модули без изменения ядра.
- **Модульный монолит:** без микросервисов, но с чёткими границами модулей.

## Команды

`make help` — все команды; `make test`, `make lint`, `make format`.
