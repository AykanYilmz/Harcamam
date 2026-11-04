# Two images from one file:
#   --target dev   editable install with test tools; docker-compose.yml bind-mounts the source
#   --target prod  (default) only the app and its runtime dependencies, run as a non-root user

FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app


FROM base AS dev
COPY . .
RUN pip install -e ".[dev]"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# Builds wheels for the app and its dependencies; nothing from this stage but /wheels ships.
FROM base AS build
COPY pyproject.toml ./
COPY app ./app
RUN pip wheel --wheel-dir /wheels .


FROM base AS prod
RUN useradd --system --uid 10001 --no-create-home app
# Mounted only while installing, so the wheels don't stay behind in an image layer.
RUN --mount=type=bind,from=build,source=/wheels,target=/wheels \
    pip install --no-index /wheels/*.whl
# Migrations run from here at startup; the app itself is installed in site-packages.
COPY alembic.ini ./
COPY alembic ./alembic
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
# Behind the nginx in the web image: trust its X-Forwarded-* headers so client IPs and https
# are seen correctly. `exec` makes uvicorn PID 1, so it receives the stop signal.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${WEB_CONCURRENCY:-2} --proxy-headers --forwarded-allow-ips='*'"]
