# 基础阶段：安装系统依赖
FROM python:3.9-slim as base

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.4.2

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python -

# 开发阶段：安装所有依赖
FROM base as development

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . .

CMD ["poetry", "run", "uvicorn", "src.gateway.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# 构建阶段：安装生产依赖
FROM base as builder

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-dev

COPY . .

RUN poetry build

# 生产阶段：最小化镜像
FROM python:3.9-slim as production

WORKDIR /app

COPY --from=builder /app/dist/*.whl /app/
COPY docker/gateway/entrypoint.sh /app/

RUN pip install --no-cache-dir /app/*.whl \
    && rm /app/*.whl \
    && useradd -r -u 1000 appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "src.gateway.main:app", "--host", "0.0.0.0", "--port", "8000"] 