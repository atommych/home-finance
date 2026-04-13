FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONPATH=/app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock* ./

# --- Development target ---
FROM base AS dev
RUN uv sync --frozen 2>/dev/null || uv sync
COPY app/ ./app/
COPY tests/ ./tests/
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1
CMD ["uv", "run", "streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

# --- Production target ---
FROM base AS production
RUN uv sync --frozen --no-dev 2>/dev/null || uv sync --no-dev
COPY app/ ./app/
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1
CMD ["uv", "run", "streamlit", "run", "app/main.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
