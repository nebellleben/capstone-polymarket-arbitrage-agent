#!/bin/bash

echo "=== Starting Polymarket Arbitrage Agent ==="
echo "Environment: ${ENVIRONMENT:-not set}"
echo "PWD: $(pwd)"
# Use Railway's PORT if set, otherwise fall back to WEB_SERVER_PORT or 8080
echo "Railway PORT: ${PORT:-not set}"
export WEB_SERVER_PORT=${PORT:-${WEB_SERVER_PORT:-8080}}
echo "Web Server Port: $WEB_SERVER_PORT"
echo "========================================="

# Trap signals for graceful shutdown
cleanup() {
    echo ""
    echo "Received shutdown signal, stopping services..."

    # Kill background processes
    if [ -n "$WORKER_PID" ]; then
        echo "Stopping worker process (PID: $WORKER_PID)..."
        kill $WORKER_PID 2>/dev/null || true
    fi

    if [ -n "$WEB_PID" ]; then
        echo "Stopping web server process (PID: $WEB_PID)..."
        kill $WEB_PID 2>/dev/null || true
    fi

    # Wait for processes to terminate (with timeout)
    TIMEOUT=10
    ELAPSED=0

    while [ $ELAPSED -lt $TIMEOUT ]; do
        if ! kill -0 $WORKER_PID 2>/dev/null && ! kill -0 $WEB_PID 2>/dev/null; then
            break
        fi
        sleep 1
        ELAPSED=$((ELAPSED + 1))
    done

    # Force kill if still running
    if kill -0 $WORKER_PID 2>/dev/null; then
        echo "Worker still running, force killing..."
        kill -9 $WORKER_PID 2>/dev/null || true
    fi

    if kill -0 $WEB_PID 2>/dev/null; then
        echo "Web server still running, force killing..."
        kill -9 $WEB_PID 2>/dev/null || true
    fi

    echo "All services stopped successfully"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Initialize database
echo "Initializing database..."
python -m src.database.connection init

# Start background worker
echo "Starting detection worker..."
python -m src.workflows.mvp_workflow &
WORKER_PID=$!

# Start web server
echo "Starting web server on port ${WEB_SERVER_PORT:-8080}..."
uvicorn src.api.main:app \
    --host 0.0.0.0 \
    --port ${WEB_SERVER_PORT:-8080} \
    --log-level info 2>&1 &
WEB_PID=$!

# Verify web server started
sleep 2
if ! kill -0 $WEB_PID 2>/dev/null; then
    echo "ERROR: Web server failed to start or exited immediately"
    exit 1
fi

echo ""
echo "✓ Services started successfully"
echo "  - Worker PID: $WORKER_PID"
echo "  - Web Server PID: $WEB_PID"
echo "  - Health check: http://localhost:${WEB_SERVER_PORT:-8080}/api/health"
echo ""

# Wait for any process to exit
wait $WORKER_PID $WEB_PID

# If we reach here, one of the processes exited unexpectedly
EXIT_CODE=$?
echo "ERROR: One of the services exited unexpectedly (exit code: $EXIT_CODE)"
cleanup
