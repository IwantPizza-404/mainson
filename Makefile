# Основные команды разработки. `make help` — список.
COMPOSE = docker compose -f infra/docker-compose.yml
BACK = cd backend && uv run
FRONT = cd frontend && pnpm

.PHONY: help up down setup migrate superuser seed messages api-types backend frontend test lint format

help:  ## Показать команды
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-10s %s\n", $$1, $$2}'

up:  ## Поднять инфраструктуру (Postgres, Redis, Meilisearch, Mailpit)
	$(COMPOSE) up -d --wait

down:  ## Остановить инфраструктуру
	$(COMPOSE) down

setup:  ## Первичная установка зависимостей
	cd backend && uv sync && ([ -f .env ] || cp .env.example .env)
	cd frontend && pnpm install && ([ -f .env ] || cp .env.example .env)

migrate:  ## Применить миграции и скомпилировать переводы
	$(BACK) python manage.py migrate
	$(BACK) python manage.py compilemessages --ignore=.venv

seed:  ## Справочники каталога + демо-товары
	$(BACK) python manage.py seed_catalog --demo

messages:  ## Обновить и скомпилировать переводы бэкенда (ru, uz)
	$(BACK) python manage.py makemessages -l ru -l uz --ignore=.venv --ignore="*/tests/*" --no-obsolete
	$(BACK) python manage.py compilemessages --ignore=.venv

api-types:  ## Сгенерировать TS-типы API для фронтенда из OpenAPI-схемы
	$(BACK) python manage.py export_openapi_schema --api config.api.api --output ../frontend/openapi.json --indent 2
	$(FRONT) openapi-typescript openapi.json -o app/types/api.d.ts

superuser:  ## Создать администратора
	$(BACK) python manage.py createsuperuser

backend:  ## Запустить Django (http://localhost:8000/admin)
	$(BACK) python manage.py runserver 8000

frontend:  ## Запустить Nuxt (http://localhost:3000)
	$(FRONT) dev

test:  ## Тесты
	$(BACK) pytest
	$(FRONT) typecheck

lint:  ## Линтеры
	$(BACK) ruff check .
	$(BACK) ruff format --check .
	$(BACK) mypy apps config
	$(FRONT) lint

format:  ## Автоформатирование
	$(BACK) ruff check --fix .
	$(BACK) ruff format .
	$(FRONT) lint --fix
