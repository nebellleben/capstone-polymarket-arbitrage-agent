#!/bin/bash

# Deployment Script for Polymarket Arbitrage Agent MVP
# Supports: Railway, Render, and Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="polymarket-arbitrage-agent"
DOCKER_IMAGE="polymarket-arbitrage-agent"
CONTAINER_NAME="${PROJECT_NAME}-mvp"

# Function to print colored output
print_color() {
    local color=$1
    shift
    echo -e "${color}$*${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check environment variables
check_env_vars() {
    print_color $YELLOW "Checking environment variables..."

    required_vars=("BRAVE_API_KEY" "ANTHROPIC_API_KEY")
    missing_vars=()

    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done

    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_color $RED "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        print_color $YELLOW "\nSet them in .env file or export them:"
        echo "  export BRAVE_API_KEY=your_key_here"
        echo "  export ANTHROPIC_API_KEY=your_key_here"
        return 1
    fi

    print_color $GREEN "✓ All required environment variables set"
    return 0
}

# Docker Compose Deployment
deploy_docker_compose() {
    print_color $YELLOW "Deploying with Docker Compose..."

    check_env_vars || exit 1

    # Build and start
    docker-compose down 2>/dev/null || true
    docker-compose build
    docker-compose up -d

    print_color $GREEN "✓ Deployed with Docker Compose"
    echo "View logs: docker-compose logs -f"
    echo "Stop: docker-compose down"
}

# Railway Deployment
deploy_railway() {
    print_color $YELLOW "Deploying to Railway..."

    if ! command_exists railway; then
        print_color $RED "Railway CLI not installed"
        echo "Install with: npm install -g @railway/cli"
        exit 1
    fi

    # Login
    print_color $YELLOW "Logging into Railway..."
    railway login || true

    # Check if project exists
    if railway list 2>/dev/null | grep -q "$PROJECT_NAME"; then
        print_color $GREEN "✓ Railway project exists"
    else
        print_color $YELLOW "Creating Railway project..."
        railway init
    fi

    # Set environment variables
    print_color $YELLOW "Setting environment variables..."
    railway variables set BRAVE_API_KEY="$BRAVE_API_KEY"
    railway variables set ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
    railway variables set ENVIRONMENT=production
    railway variables set LOG_LEVEL=INFO

    # Deploy
    print_color $YELLOW "Deploying to Railway..."
    railway up

    print_color $GREEN "✓ Deployed to Railway"
    print_color $YELLOW "View logs: railway logs"
    print_color $YELLOW "Open dashboard: railway open"
}

# Render Deployment
deploy_render() {
    print_color $YELLOW "Deploying to Render..."

    if ! command_exists render; then
        print_color $RED "Render CLI not installed"
        echo "Install with: npm install -g @render/cli"
        exit 1
    fi

    # Login
    print_color $YELLOW "Logging into Render..."
    render login || true

    # Deploy
    print_color $YELLOW "Deploying to Render..."
    render deploy

    print_color $GREEN "✓ Deployed to Render"
    print_color $YELLOW "View logs: render logs -f"
    print_color $YELLOW "Open dashboard: render open"
}

# Build Docker Image Locally
build_docker() {
    print_color $YELLOW "Building Docker image..."

    docker build -t "$DOCKER_IMAGE:latest" .

    print_color $GREEN "✓ Docker image built: $DOCKER_IMAGE:latest"
}

# Run Docker Container Locally
run_docker() {
    print_color $YELLOW "Running Docker container..."

    check_env_vars || exit 1

    # Stop existing container
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true

    # Run new container
    docker run -d \
        --name "$CONTAINER_NAME" \
        --restart unless-stopped \
        -e BRAVE_API_KEY="$BRAVE_API_KEY" \
        -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
        -e ENVIRONMENT=production \
        -e LOG_LEVEL=INFO \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/alerts:/app/alerts" \
        "$DOCKER_IMAGE:latest"

    print_color $GREEN "✓ Container started: $CONTAINER_NAME"
    echo "View logs: docker logs -f $CONTAINER_NAME"
    echo "Stop: docker stop $CONTAINER_NAME"
}

# Health Check
health_check() {
    print_color $YELLOW "Checking health..."

    if docker ps | grep -q "$CONTAINER_NAME"; then
        print_color $GREEN "✓ Container is running"
        docker logs --tail 50 "$CONTAINER_NAME"
    else
        print_color $RED "✗ Container is not running"
        return 1
    fi
}

# Show usage
usage() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Commands:
  docker-compose    Deploy with Docker Compose (local)
  railway          Deploy to Railway
  render           Deploy to Render
  build            Build Docker image only
  run              Run Docker container only
  health           Check container health
  help             Show this help

Environment Variables:
  BRAVE_API_KEY         Required (Brave Search API)
  ANTHROPIC_API_KEY     Required (Anthropic API)

Examples:
  # Local deployment
  $0 docker-compose

  # Build and run locally
  $0 build
  $0 run

  # Deploy to Railway
  $0 railway

  # Deploy to Render
  $0 render

EOF
}

# Main script
main() {
    local command=${1:-help}

    case "$command" in
        docker-compose)
            deploy_docker_compose
            ;;
        railway)
            deploy_railway
            ;;
        render)
            deploy_render
            ;;
        build)
            build_docker
            ;;
        run)
            run_docker
            ;;
        health)
            health_check
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            print_color $RED "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

main "$@"
