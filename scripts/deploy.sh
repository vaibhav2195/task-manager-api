#!/usr/bin/env bash
set -euo pipefail

# Configuration
APP_NAME="task_manager_api"
IMAGE_NAME="task-manager-api"
PORT=8000
HEALTH_CHECK_SCRIPT="$(dirname "$0")/health_check.sh"

# Colors for terminal output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTION]

Options:
  --deploy      Build and deploy the latest Docker container.
  --rollback    Rollback to the backup/previous image container.
  --status      Check current container status and health.
  --help        Display this help message.

Permissions Note: Make sure executable permissions are set via:
  chmod +x scripts/deploy.sh scripts/health_check.sh
EOF
    exit 0
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH."
        exit 1
    fi
}

deploy() {
    log_info "Starting deployment process for ${APP_NAME}..."

    check_docker

    # Tag existing container as backup before update if running
    if [ "$(docker ps -aq -f name=^/${APP_NAME}$)" ]; then
        log_info "Creating backup tag of current container..."
        docker commit "${APP_NAME}" "${IMAGE_NAME}:backup" || log_warn "Could not commit backup image."
        log_info "Stopping existing container..."
        docker stop "${APP_NAME}" || true
        docker rm "${APP_NAME}" || true
    fi

    log_info "Building new Docker image: ${IMAGE_NAME}:latest..."
    docker build -t "${IMAGE_NAME}:latest" .

    log_info "Starting container on port ${PORT}..."
    docker run -d \
        --name "${APP_NAME}" \
        -p "${PORT}:${PORT}" \
        -e ENVIRONMENT=production \
        -e REPOSITORY_TYPE=sqlite \
        -e SQLITE_DB_PATH=/app/tasks.db \
        --restart unless-stopped \
        "${IMAGE_NAME}:latest"

    log_info "Waiting for service to initialize..."
    sleep 3

    log_info "Running post-deployment health check..."
    if [ -f "$HEALTH_CHECK_SCRIPT" ]; then
        bash "$HEALTH_CHECK_SCRIPT" "http://localhost:${PORT}"
    else
        curl -s -f "http://localhost:${PORT}/health" | grep '"status": "ok"'
    fi

    log_success "Deployment completed successfully!"
}

rollback() {
    log_warn "Initiating rollback procedure..."
    check_docker

    if ! docker image inspect "${IMAGE_NAME}:backup" &> /dev/null; then
        log_error "No backup image (${IMAGE_NAME}:backup) found to rollback to!"
        exit 1
    fi

    log_info "Stopping broken container..."
    docker stop "${APP_NAME}" || true
    docker rm "${APP_NAME}" || true

    log_info "Starting backup container image..."
    docker run -d \
        --name "${APP_NAME}" \
        -p "${PORT}:${PORT}" \
        -e ENVIRONMENT=production \
        -e REPOSITORY_TYPE=sqlite \
        --restart unless-stopped \
        "${IMAGE_NAME}:backup"

    log_info "Running health check on rolled-back container..."
    bash "$HEALTH_CHECK_SCRIPT" "http://localhost:${PORT}"
    log_success "Rollback executed successfully!"
}

status() {
    log_info "Checking container status..."
    check_docker
    if [ "$(docker ps -q -f name=^/${APP_NAME}$)" ]; then
        log_success "Container ${APP_NAME} is RUNNING."
        docker ps -f name=^/${APP_NAME}$
        echo ""
        log_info "Health Check Result:"
        bash "$HEALTH_CHECK_SCRIPT" "http://localhost:${PORT}"
    else
        log_warn "Container ${APP_NAME} is NOT running."
    fi
}

# Parse Command Line Arguments
ACTION="${1:---deploy}"

case "$ACTION" in
    --deploy|deploy)
        deploy
        ;;
    --rollback|rollback)
        rollback
        ;;
    --status|status)
        status
        ;;
    --help|help|-h)
        usage
        ;;
    *)
        log_error "Unknown option: $ACTION"
        usage
        ;;
esac
