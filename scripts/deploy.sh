#!/usr/bin/env bash
# Деплой на сервер: обновить код, собрать образы, применить миграции, перезапустить.
# Запуск на сервере из корня проекта: ./scripts/deploy.sh
set -euo pipefail
cd "$(dirname "$0")/.."

COMPOSE=(docker compose -f infra/docker-compose.prod.yml --env-file infra/.env.prod)

if [[ ! -f infra/.env.prod ]]; then
  echo "Нет infra/.env.prod — скопируйте infra/.env.prod.example и заполните" >&2
  exit 1
fi

echo "→ Обновление кода"
git pull --ff-only

echo "→ Сборка образов"
"${COMPOSE[@]}" build

echo "→ Миграции"
"${COMPOSE[@]}" run --rm backend python manage.py migrate --noinput

echo "→ Перезапуск"
"${COMPOSE[@]}" up -d --remove-orphans

echo "→ Поисковый индекс"
"${COMPOSE[@]}" exec -T backend python manage.py search_reindex

docker image prune -f >/dev/null
echo "✓ Готово"
