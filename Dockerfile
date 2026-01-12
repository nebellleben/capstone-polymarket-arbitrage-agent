# Multi-stage Dockerfile for Polymarket Arbitrage Agent MVP
# Stage 1: Builder
FROM python:3.11-slim as builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim as runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 arbitrage && \
    mkdir -p /app /app/logs && \
    chown -R arbitrage:arbitrage /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=arbitrage:arbitrage . .

# Create logs directory
RUN mkdir -p /app/logs && \
    chown -R arbitrage:arbitrage /app/logs

# Switch to non-root user
USER arbitrage

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the application
CMD ["python", "-m", "src.workflows.mvp_workflow"]
