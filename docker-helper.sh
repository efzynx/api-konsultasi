#!/bin/bash

# Docker Helper Script for API Konsultasi
# This script helps manage Docker containers and avoid port conflicts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill processes on a port
kill_port() {
    local port=$1
    print_status "Checking for processes on port $port..."
    
    if check_port $port; then
        print_warning "Port $port is in use. Attempting to free it..."
        lsof -ti:$port | xargs -r kill -9 2>/dev/null || true
        sleep 2
        
        if check_port $port; then
            print_error "Failed to free port $port. Please manually stop the process."
            lsof -i :$port
            return 1
        else
            print_success "Port $port is now free."
        fi
    else
        print_success "Port $port is already free."
    fi
}

# Function to find available port
find_available_port() {
    local start_port=$1
    local port=$start_port
    
    while check_port $port; do
        port=$((port + 1))
        if [ $port -gt $((start_port + 10)) ]; then
            print_error "Could not find available port in range $start_port-$((start_port + 10))"
            return 1
        fi
    done
    
    echo $port
}

# Function to clean up Docker containers
cleanup_containers() {
    print_status "Cleaning up existing containers..."
    
    # Stop and remove containers with our project name
    docker ps -a --filter "name=api_konsultasi" --format "{{.Names}}" | xargs -r docker stop 2>/dev/null || true
    docker ps -a --filter "name=api_konsultasi" --format "{{.Names}}" | xargs -r docker rm 2>/dev/null || true
    
    # Also clean up test containers
    docker ps -a --filter "name=test-container" --format "{{.Names}}" | xargs -r docker stop 2>/dev/null || true
    docker ps -a --filter "name=test-container" --format "{{.Names}}" | xargs -r docker rm 2>/dev/null || true
    
    print_success "Container cleanup completed."
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image..."
    docker build -t api-konsultasi:latest .
    print_success "Docker image built successfully."
}

# Function to run with Docker Compose
run_compose() {
    local port=${1:-5001}
    
    print_status "Starting application with Docker Compose on port $port..."
    
    # Kill any processes on the target port
    kill_port $port
    
    # Update the override file with the specified port
    cat > docker-compose.override.yml << EOF
version: '3.8'

services:
  server:
    ports:
      - "$port:5000"
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    volumes:
      - .:/app
    command: python run.py
EOF

    # Start with compose
    docker-compose up --build -d
    
    print_success "Application started on http://localhost:$port"
    print_status "API Documentation: http://localhost:$port/api/v1/docs/"
    print_status "Health Check: http://localhost:$port/api/v1/auth/health"
}

# Function to run tests in Docker
run_tests() {
    print_status "Running tests in Docker container..."
    
    # Build test image
    docker build -t api-konsultasi:test .
    
    # Find available port
    local port=$(find_available_port 5000)
    print_status "Using port $port for testing..."
    
    # Create test environment
    cat > .env.test << EOF
SECRET_KEY=test-secret-key
DATABASE_URL=sqlite:///test.db
JWT_SECRET_KEY=test-jwt-secret-key
FLASK_ENV=testing
EOF

    # Run test container
    docker run --rm --name test-container -p $port:5000 --env-file .env.test api-konsultasi:test &
    local container_pid=$!
    
    # Wait for container to start
    sleep 10
    
    # Test the application
    if curl -f http://localhost:$port/api/v1/auth/health >/dev/null 2>&1; then
        print_success "Container test passed!"
    else
        print_error "Container test failed!"
        docker logs test-container 2>/dev/null || true
    fi
    
    # Cleanup
    docker stop test-container 2>/dev/null || true
    rm -f .env.test
}

# Function to show logs
show_logs() {
    print_status "Showing application logs..."
    docker-compose logs -f server
}

# Function to stop services
stop_services() {
    print_status "Stopping all services..."
    docker-compose down
    cleanup_containers
    kill_port 5000
    kill_port 5001
    print_success "All services stopped."
}

# Main script logic
case "${1:-help}" in
    "build")
        build_image
        ;;
    "start")
        run_compose ${2:-5001}
        ;;
    "test")
        run_tests
        ;;
    "logs")
        show_logs
        ;;
    "stop")
        stop_services
        ;;
    "cleanup")
        cleanup_containers
        ;;
    "port-check")
        port=${2:-5000}
        if check_port $port; then
            print_warning "Port $port is in use:"
            lsof -i :$port
        else
            print_success "Port $port is available."
        fi
        ;;
    "kill-port")
        port=${2:-5000}
        kill_port $port
        ;;
    "help"|*)
        echo "Docker Helper Script for API Konsultasi"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  build                 Build Docker image"
        echo "  start [port]          Start application with Docker Compose (default port: 5001)"
        echo "  test                  Run tests in Docker container"
        echo "  logs                  Show application logs"
        echo "  stop                  Stop all services and cleanup"
        echo "  cleanup               Clean up Docker containers"
        echo "  port-check [port]     Check if port is in use (default: 5000)"
        echo "  kill-port [port]      Kill processes on port (default: 5000)"
        echo "  help                  Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 start              # Start on port 5001"
        echo "  $0 start 8080         # Start on port 8080"
        echo "  $0 test               # Run container tests"
        echo "  $0 kill-port 5000     # Free up port 5000"
        ;;
esac
