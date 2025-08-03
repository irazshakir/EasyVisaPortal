#!/bin/bash

# Easy Visa Portal - Development Setup Script

set -e

echo "🚀 Setting up Easy Visa Portal Development Environment..."

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

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"
}

# Check if Docker Compose is installed
check_docker_compose() {
    print_status "Checking Docker Compose installation..."
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose is installed"
}

# Create environment files
create_env_files() {
    print_status "Creating environment files..."
    
    # Frontend .env
    if [ ! -f "frontend/.env" ]; then
        cat > frontend/.env << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_BOT_API_URL=http://localhost:8001
REACT_APP_WHATSAPP_URL=http://localhost:8001/visa-evaluation
EOF
        print_success "Created frontend/.env"
    fi
    
    # Backend .env
    if [ ! -f "backend/.env" ]; then
        cat > backend/.env << EOF
DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production
DATABASE_URL=postgresql://postgres:password@db:5432/visa_portal
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EOF
        print_success "Created backend/.env"
    fi
    
    # Bot environment files
    if [ ! -f "bots/visa_evaluation_bot/.env" ]; then
        cat > bots/visa_evaluation_bot/.env << EOF
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
WHATSAPP_TOKEN=your-whatsapp-token
DATABASE_URL=postgresql://postgres:password@db:5432/visa_portal
REDIS_URL=redis://redis:6379/0
EOF
        print_success "Created bots/visa_evaluation_bot/.env"
    fi
    
    if [ ! -f "bots/document_preparation_bot/.env" ]; then
        cat > bots/document_preparation_bot/.env << EOF
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
DATABASE_URL=postgresql://postgres:password@db:5432/visa_portal
REDIS_URL=redis://redis:6379/0
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
EOF
        print_success "Created bots/document_preparation_bot/.env"
    fi
}

# Install frontend dependencies
setup_frontend() {
    print_status "Setting up frontend..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
        print_success "Frontend dependencies installed"
    else
        print_success "Frontend dependencies already installed"
    fi
    
    cd ..
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment and install dependencies
    print_status "Installing backend dependencies..."
    source venv/bin/activate
    pip install -r requirements/development.txt
    print_success "Backend dependencies installed"
    
    cd ..
}

# Setup bot services
setup_bots() {
    print_status "Setting up bot services..."
    
    # Visa Evaluation Bot
    cd bots/visa_evaluation_bot
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt
    cd ../..
    
    # Document Preparation Bot
    cd bots/document_preparation_bot
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt
    cd ../..
    
    print_success "Bot services setup completed"
}

# Build Docker images
build_docker_images() {
    print_status "Building Docker images..."
    
    # Build frontend
    print_status "Building frontend image..."
    docker build -t visa-portal/frontend:latest ./frontend
    
    # Build backend
    print_status "Building backend image..."
    docker build -t visa-portal/backend:latest ./backend
    
    # Build bot images
    print_status "Building bot images..."
    docker build -t visa-portal/visa-evaluation-bot:latest ./bots/visa_evaluation_bot
    docker build -t visa-portal/document-preparation-bot:latest ./bots/document_preparation_bot
    
    print_success "All Docker images built successfully"
}

# Start services
start_services() {
    print_status "Starting services with Docker Compose..."
    
    cd infrastructure/docker
    docker-compose -f docker-compose.dev.yml up -d
    
    print_success "Services started successfully"
    print_status "Services are running on:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend API: http://localhost:8000"
    echo "  - Visa Evaluation Bot: http://localhost:8001"
    echo "  - Document Preparation Bot: http://localhost:8002"
    echo "  - MinIO Console: http://localhost:9001"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
    
    cd ../..
}

# Main setup function
main() {
    print_status "Starting Easy Visa Portal setup..."
    
    # Check prerequisites
    check_docker
    check_docker_compose
    
    # Create environment files
    create_env_files
    
    # Setup local development
    setup_frontend
    setup_backend
    setup_bots
    
    # Build Docker images
    build_docker_images
    
    # Start services
    start_services
    
    print_success "🎉 Easy Visa Portal setup completed successfully!"
    print_warning "Please update the .env files with your actual API keys and secrets before using the application."
    
    echo ""
    print_status "Next steps:"
    echo "1. Update API keys in the .env files"
    echo "2. Run database migrations: docker-compose exec backend python manage.py migrate"
    echo "3. Create superuser: docker-compose exec backend python manage.py createsuperuser"
    echo "4. Access the application at http://localhost:3000"
}

# Run main function
main "$@" 