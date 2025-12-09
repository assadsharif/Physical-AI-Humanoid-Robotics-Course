# Multi-stage optimized build for the FastAPI backend
ARG PYTHON_VERSION=3.11
ARG PYTHON_VARIANT=slim

# Stage 1: Builder - compile dependencies
FROM python:${PYTHON_VERSION}-${PYTHON_VARIANT} as builder

WORKDIR /app

# Install build dependencies (gcc for native extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements for better layer caching
COPY backend/requirements.txt .

# Create virtual environment with optimizations
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip wheel setuptools && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Base production image
FROM python:${PYTHON_VERSION}-${PYTHON_VARIANT} as production-base

WORKDIR /app

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables for Python optimization
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Stage 3: Development image (includes dev tools)
FROM production-base as development

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    git \
    && rm -rf /var/lib/apt/lists/*
USER appuser

# Copy all source code
COPY --chown=appuser:appuser backend/src ./src
COPY --chown=appuser:appuser backend/migrations ./migrations
COPY --chown=appuser:appuser backend/.env.example .env

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 4: Production image (minimal and secure)
FROM production-base as production

# Copy only essential files from builder
COPY --chown=appuser:appuser backend/src ./src
COPY --chown=appuser:appuser backend/.env.example .env

# Health check using wget (lighter than curl)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

EXPOSE 8000

# Run as non-root user (already set in production-base)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
