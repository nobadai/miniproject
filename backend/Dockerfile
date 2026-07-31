# syntax=docker/dockerfile:1

# 목적: Python 3.12 FastAPI 애플리케이션 Image를 생성한다.
# 주요 역할: uv.lock에 맞춰 Dependency를 설치하고 ASGI Server를 실행한다.

FROM ghcr.io/astral-sh/uv:0.12.0 AS uv

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# 업로드 오디오를 mono 16kHz WAV로 정규화하는 데 ffmpeg 실행 파일이 필요하다.
RUN apt-get update \
    && apt-get install --no-install-recommends -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY app ./app
COPY resources ./resources

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
