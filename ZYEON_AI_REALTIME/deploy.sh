#!/bin/bash

# ZYEON AI Enhanced - Deployment Script
# This script handles the complete deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if required commands exist
check_dependencies() {
    log "Checking dependencies..."
    
    local deps=("node" "npm" "python3" "pip")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        error "Missing dependencies: ${missing[*]}"
        error "Please install the missing dependencies and try again."
        exit 1
    fi
    
    success "All dependencies found"
}

# Check environment variables
check_environment() {
    log "Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        warning ".env file not found. Creating template..."
        cat > .env << EOF
# ZYEON AI Enhanced Configuration
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
FLASK_ENV=production
SECRET_KEY=zyeon_ai_secret_key_2024_enhanced
PORT=5000
EOF
        warning "Please edit .env file with your actual configuration before running again."
        exit 1
    fi
    
    # Source environment variables
    source .env
    
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
        warning "OPENAI_API_KEY not configured properly in .env file"
    fi
    
    if [ -z "$MONGODB_URI" ] || [[ "$MONGODB_URI" == *"username:password"* ]]; then
        warning "MONGODB_URI not configured properly in .env file"
    fi
    
    success "Environment configuration checked"
}

# Install frontend dependencies
install_frontend() {
    log "Installing frontend dependencies..."
    
    cd frontend
    
    if [ ! -f "package.json" ]; then
        error "Frontend package.json not found"
        exit 1
    fi
    
    npm install --legacy-peer-deps
    success "Frontend dependencies installed"
    
    cd ..
}

# Build frontend
build_frontend() {
    log "Building frontend..."
    
    cd frontend
    npm run build
    success "Frontend built successfully"
    
    # Copy to backend static folder
    log "Copying frontend build to backend..."
    mkdir -p ../backend/src/static
    cp -r dist/* ../backend/src/static/
    success "Frontend copied to backend static folder"
    
    cd ..
}

# Install backend dependencies
install_backend() {
    log "Installing backend dependencies..."
    
    cd backend
    
    if [ ! -f "requirements.txt" ]; then
        error "Backend requirements.txt not found"
        exit 1
    fi
    
    # Install system dependencies if on Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        log "Installing system dependencies..."
        sudo apt-get update
        sudo apt-get install -y build-essential portaudio19-dev python3-dev espeak espeak-data libespeak1 libespeak-dev
    fi
    
    pip install -r requirements.txt
    success "Backend dependencies installed"
    
    cd ..
}

# Run tests
run_tests() {
    log "Running tests..."
    
    cd backend
    
    # Create logs directory
    mkdir -p logs
    
    # Test import of main modules
    python -c "
import sys
sys.path.insert(0, 'src')
try:
    from models.conversation import ConversationModel
    from services.ai_service import ZyeonAIService
    from services.voice_service import VoiceService
    print('✓ All modules import successfully')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"
    
    success "Tests passed"
    cd ..
}

# Start the application
start_application() {
    log "Starting ZYEON AI Enhanced..."
    
    cd backend
    
    # Create logs directory
    mkdir -p logs
    
    # Start the application
    python src/main.py
}

# Docker deployment
deploy_docker() {
    log "Deploying with Docker..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker not found. Please install Docker first."
        exit 1
    fi
    
    # Build Docker image
    log "Building Docker image..."
    docker build -t zyeon-ai-enhanced .
    
    # Run with Docker Compose if available
    if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
        log "Starting with Docker Compose..."
        docker-compose up -d
        success "ZYEON AI Enhanced started with Docker Compose"
        log "Application available at http://localhost:5000"
    else
        # Run with Docker directly
        log "Starting with Docker..."
        docker run -d \
            --name zyeon-ai-enhanced \
            -p 5000:5000 \
            --env-file .env \
            zyeon-ai-enhanced
        success "ZYEON AI Enhanced started with Docker"
        log "Application available at http://localhost:5000"
    fi
}

# Production deployment
deploy_production() {
    log "Deploying for production..."
    
    # Set production environment
    export FLASK_ENV=production
    
    # Install dependencies
    install_frontend
    build_frontend
    install_backend
    run_tests
    
    # Start with production server (gunicorn)
    if command -v gunicorn &> /dev/null; then
        log "Starting with Gunicorn..."
        cd backend
        gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 4 --worker-class eventlet src.main:app
    else
        warning "Gunicorn not found. Installing..."
        pip install gunicorn
        cd backend
        gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 4 --worker-class eventlet src.main:app
    fi
}

# Development deployment
deploy_development() {
    log "Deploying for development..."
    
    # Set development environment
    export FLASK_ENV=development
    
    # Install dependencies
    install_frontend
    build_frontend
    install_backend
    run_tests
    
    # Start development server
    start_application
}

# Show usage
show_usage() {
    echo "ZYEON AI Enhanced - Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev         Deploy for development (default)"
    echo "  prod        Deploy for production"
    echo "  docker      Deploy with Docker"
    echo "  build       Build frontend and backend only"
    echo "  test        Run tests only"
    echo "  clean       Clean build artifacts"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev      # Start development server"
    echo "  $0 prod     # Start production server"
    echo "  $0 docker   # Deploy with Docker"
    echo ""
}

# Clean build artifacts
clean() {
    log "Cleaning build artifacts..."
    
    # Clean frontend
    if [ -d "frontend/dist" ]; then
        rm -rf frontend/dist
        log "Cleaned frontend/dist"
    fi
    
    if [ -d "frontend/node_modules" ]; then
        rm -rf frontend/node_modules
        log "Cleaned frontend/node_modules"
    fi
    
    # Clean backend
    if [ -d "backend/src/static" ]; then
        rm -rf backend/src/static/*
        log "Cleaned backend/src/static"
    fi
    
    if [ -d "backend/__pycache__" ]; then
        find backend -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        log "Cleaned Python cache files"
    fi
    
    success "Cleanup completed"
}

# Main script logic
main() {
    local command="${1:-dev}"
    
    case "$command" in
        "dev"|"development")
            check_dependencies
            check_environment
            deploy_development
            ;;
        "prod"|"production")
            check_dependencies
            check_environment
            deploy_production
            ;;
        "docker")
            check_environment
            deploy_docker
            ;;
        "build")
            check_dependencies
            install_frontend
            build_frontend
            install_backend
            ;;
        "test")
            check_dependencies
            run_tests
            ;;
        "clean")
            clean
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"

