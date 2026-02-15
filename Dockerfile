# Akura AI - Docker Image
# Multi-stage build for optimized container size

# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.11-slim as runtime

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash akura
USER akura

# Copy installed packages from builder
COPY --from=builder /root/.local /home/akura/.local
ENV PATH=/home/akura/.local/bin:$PATH

# Copy application code
COPY --chown=akura:akura . .

# Set environment variables (PORT overridden by Cloud Run to 8080)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=8000

# Expose default port (Cloud Run uses 8080 via env)
EXPOSE 8000 8080

# Health check uses PORT so it works on both local (8000) and Cloud Run (8080)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD sh -c "curl -f http://localhost:${PORT:-8000}/api/v1/health || exit 1"

# Run the application (Shell form to expand PORT variable)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
