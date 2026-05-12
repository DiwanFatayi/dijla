# syntax=docker/dockerfile:1.7
# ---- builder ----
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_NO_CACHE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv==0.9.5

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src

RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache .

# ---- runtime ----
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/opt/venv/bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system dijla && useradd --system --gid dijla --create-home dijla

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY --chown=dijla:dijla pyproject.toml README.md ./
COPY --chown=dijla:dijla src ./src

USER dijla

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s \
    CMD curl -fsS http://127.0.0.1:8000/healthz || exit 1

CMD ["uvicorn", "dijla.main:app", "--host", "0.0.0.0", "--port", "8000"]
