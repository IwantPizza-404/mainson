# Maison — maison.uz

Интернет-магазин часов. Перед работой прочитать:
- [docs/TZ.md](docs/TZ.md) — техническое задание
- [docs/ROADMAP.md](docs/ROADMAP.md) — план и текущий статус
- [docs/DECISIONS.md](docs/DECISIONS.md) — почему выбраны такие решения (не переигрывать без причины)
- [docs/CLIENT.md](docs/CLIENT.md) — ответы заказчика и открытые вопросы
- [docs/DEPLOY.md](docs/DEPLOY.md) — сервер, деплой, бэкапы

Общение с разработчиком — на русском. Комментарии в коде — на русском.

## Структура

- `backend/` — Django 5.2 + Ninja + Unfold. Модули в `apps/`: `core`, `catalog`, `currency`, `orders`, `content`.
  Каждый модуль: `models.py`, `services.py` (бизнес-логика), `api.py` (Ninja Router → `config/api.py`),
  `schemas.py`, `admin.py`, `translation.py` (modeltranslation), `tests/`.
- `frontend/` — Nuxt 4 + Nuxt UI 4 + Pinia + @nuxtjs/i18n. Страницы `app/pages`, компоненты `app/components`,
  сторы `app/stores`, переводы `i18n/locales/{en,ru,uz}.json`, типы API — `app/types/api.d.ts` (генерируются).
- `infra/docker-compose.yml` — локально: Postgres (порт 5433), Redis, Meilisearch, Mailpit.
- `infra/docker-compose.prod.yml` + `infra/caddy/` — продакшен; деплой `scripts/deploy.sh`.

## Команды (`make help`)

```bash
nvm use                 # Node 24
make up                 # инфраструктура в Docker
make backend            # Django :8000 (админка /admin, API /api/v1/docs)
make frontend           # Nuxt :3000
make test && make lint  # перед каждым коммитом — оба должны проходить
make api-types          # после изменения API — перегенерировать TS-типы фронтенда
make messages           # после новых строк в бэкенде — обновить переводы ru/uz
make seed               # справочники + демо-товары
```

## Правила

- Цены — только USD (`Decimal`, в JSON строкой). Пересчёт валют — только для отображения.
- Новые строки интерфейса — сразу на трёх языках: бэкенд (`make messages`, заполнить `locale/*/django.po`,
  без fuzzy), фронтенд (все три `i18n/locales/*.json`).
- Одинаковое английское слово с разным смыслом — `pgettext_lazy("контекст", ...)`.
- Фронтенд — компоненты Nuxt UI, а не самописные базовые элементы. Цвета: `ink`, `gold-*`, семантические токены Nuxt UI.
- Бизнес-логику — в `services.py`, не в API и не в админке.
- Изменение моделей — миграция в том же коммите; данные по умолчанию — data-миграцией (см. `orders/0002`).
- Тесты на каждое бизнес-правило; общий тест открывает все страницы админки (`core/tests/test_admin.py`).
- Коммиты на русском, **без** строки `Co-Authored-By` и без упоминания Claude — автор коммитов только разработчик.
