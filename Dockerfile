# Multi-stage Dockerfile for Polymarket Arbitrage Agent MVP
# Build: 2026-01-13-16:45 - Force Railway cache invalidation with latest code
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
    mkdir -p /app /app/logs /app/data && \
    chown -R arbitrage:arbitrage /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=arbitrage:arbitrage . .

# Copy and make executable the entrypoint script
COPY --chown=arbitrage:arbitrage docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Create logs and data directories
RUN mkdir -p /app/logs /app/data && \
    chown -R arbitrage:arbitrage /app/logs /app/data

# Switch to non-root user
USER arbitrage

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production
# Don't set WEB_SERVER_PORT here - let Railway's PORT take precedence
# The entrypoint script will use PORT if set, otherwise default to 8080

# Health check - check web server health endpoint
# Use PORT environment variable if set, otherwise default to 8080
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/api/health || exit 1

# Expose port for Railway routing
# Railway uses this to configure the Edge Proxy routing
EXPOSE 8080

# Run the supervisor script (starts both worker and web server)
CMD ["./docker-entrypoint.sh"]
