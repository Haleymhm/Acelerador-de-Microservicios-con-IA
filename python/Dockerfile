# ── Build stage ────────────────────────────────────────────────────────
FROM python:3.10-slim AS builder

WORKDIR /build

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.5 \
    && poetry config virtualenvs.create false

COPY pyproject.toml ./
RUN poetry install --no-root --only main --no-interaction --no-ansi

# ── Runtime stage ─────────────────────────────────────────────────────
FROM python:3.10-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/

# Non-root user for security
RUN adduser --disabled-password --no-create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
