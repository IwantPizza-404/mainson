# Сборка: зависимости, переводы, статика
FROM python:3.13-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
RUN apt-get update && apt-get install -y --no-install-recommends gettext && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY . .
ENV PATH="/app/.venv/bin:$PATH" DJANGO_SETTINGS_MODULE=config.settings.prod
# Фиктивные значения — только чтобы Django загрузился во время сборки
RUN DJANGO_SECRET_KEY=build PUBLIC_URL=http://build DATABASE_URL=sqlite:////tmp/build.db \
    sh -c "python manage.py compilemessages --ignore=.venv && python manage.py collectstatic --noinput"

# Запуск: только приложение, без компиляторов и gettext
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" DJANGO_SETTINGS_MODULE=config.settings.prod
RUN useradd --system --uid 1000 --home /app app
WORKDIR /app
COPY --from=build --chown=app:app /app /app
RUN mkdir -p /app/media && chown app:app /app/media
USER app
EXPOSE 8000
CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-"]
