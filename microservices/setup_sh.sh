#!/bin/bash

# Task Management System - Automated Setup Script
# This script sets up the microservices environment automatically

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Banner
echo -e "${BLUE}"
cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   ████████╗ █████╗ ███████╗██╗  ██╗    ███╗   ███╗ ██████╗    ║
║   ╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝    ████╗ ████║██╔════╝    ║
║      ██║   ███████║███████╗█████╔╝     ██╔████╔██║██║  ███╗   ║
║      ██║   ██╔══██║╚════██║██╔═██╗     ██║╚██╔╝██║██║   ██║   ║
║      ██║   ██║  ██║███████║██║  ██╗    ██║ ╚═╝ ██║╚██████╔╝   ║
║      ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝ ╚═════╝    ║
║                                                                ║
║            MICROSERVICES SETUP SCRIPT                         ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${GREEN}🚀 Welcome to Task Management System Setup!${NC}"
echo -e "${CYAN}This script will set up the complete microservices environment.${NC}"
echo ""

# Function to print status messages
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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to generate a random secret
generate_secret() {
    openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "$(date +%s)_$(whoami)_secret_$(shuf -i 1000-9999 -n 1)"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_deps=()
    
    if ! command_exists docker; then
        missing_deps+=("docker")
    fi
    
    if ! command_exists docker-compose; then
        missing_deps+=("docker-compose")
    fi
    
    if ! command_exists curl; then
        missing_deps+=("curl")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        echo ""
        echo "Please install the missing dependencies:"
        echo "  - Docker: https://docs.docker.com/get-docker/"
        echo "  - Docker Compose: https://docs.docker.com/compose/install/"
        echo "  - curl: Usually available in your package manager"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    print_success "All prerequisites are met!"
}

# Setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ -f .env ]; then
        print_warning ".env file already exists."
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Keeping existing .env file."
            return
        fi
    fi
    
    print_status "Creating .env file from template..."
    cp .env.example .env
    
    print_status "Generating secure secrets..."
    
    # Generate secrets
    JWT_SECRET=$(generate_secret)
    USER_SERVICE_SECRET=$(generate_secret)
    PROJECT_TASK_SERVICE_SECRET=$(generate_secret)
    COMMENT_SERVICE_SECRET=$(generate_secret)
    ATTACHMENT_SERVICE_SECRET=$(generate_secret)
    NOTIFICATION_SERVICE_SECRET=$(generate_secret)
    ACTIVITY_LOG_SERVICE_SECRET=$(generate_secret)
    REPORTING_SERVICE_SECRET=$(generate_secret)
    
    # Update .env file with generated secrets
    sed -i.bak "s/your_jwt_secret_key_here/$JWT_SECRET/g" .env
    sed -i.bak "s/your_user_service_secret_key_here/$USER_SERVICE_SECRET/g" .env
    sed -i.bak "s/your_project_task_service_secret_key_here/$PROJECT_TASK_SERVICE_SECRET/g" .env
    sed -i.bak "s/your_comment_service_secret_key_here/$COMMENT_SERVICE_SECRET/g" .env
    sed -i.bak "s/your_attachment_service_secret_key_here/$ATTACHMENT_SERVICE_SECRET/g" .env
    sed -i.bak "s/your_notification_service_secret_key_here/$NOTIFICATION_SERVICE_SECRET/g" .env
    sed -i.bak "s/your_activity_log_service_secret_key_here/$ACTIVITY_LOG_SERVICE_SECRET/g" .env
    sed -i.bak "s/your_reporting_service_secret_key_here/$REPORTING_SERVICE_SECRET/g" .env
    
    # Remove backup file
    rm -f .env.bak
    
    print_success "Environment file created with secure secrets!"
    
    # Prompt for email configuration
    echo ""
    print_status "Email configuration (for notifications):"
    echo "You can configure email settings now or later by editing the .env file."
    read -p "Do you want to configure email settings now? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        read -p "SMTP Server (e.g., smtp.gmail.com): " smtp_server
        read -p "SMTP Port (e.g., 587): " smtp_port
        read -p "Email Username: " email_username
        read -s -p "Email Password (will be hidden): " email_password
        echo
        read -p "From Email Address: " from_email
        
        # Update email settings in .env
        sed -i.bak "s/smtp.gmail.com/$smtp_server/g" .env
        sed -i.bak "s/587/$smtp_port/g" .env
        sed -i.bak "s/your_email@gmail.com/$email_username/g" .env
        sed -i.bak "s/your_app_password/$email_password/g" .env
        sed -i.bak "s/noreply@taskapp.com/$from_email/g" .env
        
        rm -f .env.bak
        print_success "Email configuration updated!"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p uploads
    mkdir -p logs
    mkdir -p backups
    mkdir -p ssl
    
    # Create .gitkeep files to preserve empty directories
    touch uploads/.gitkeep
    touch logs/.gitkeep
    touch backups/.gitkeep
    
    print_success "Directory structure created!"
}

# Setup proxy_params file for nginx
setup_nginx_config() {
    print_status "Setting up Nginx configuration..."
    
    if [ ! -f proxy_params ]; then
        cat > proxy_params << 'EOF'
# Nginx proxy parameters configuration
proxy_set_header Host $http_host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host $server_name;
proxy_set_header X-Forwarded-Port $server_port;

proxy_connect_timeout 60s;
proxy_send_timeout 60s;
proxy_read_timeout 60s;

proxy_buffering on;
proxy_buffer_size 4k;
proxy_buffers 8 4k;
proxy_busy_buffers_size 8k;

proxy_redirect off;
proxy_http_version 1.1;
proxy_set_header Connection "";

proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection $connection_upgrade;
EOF
        print_success "Nginx proxy configuration created!"
    else
        print_status "Nginx proxy configuration already exists."
    fi
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    echo "This may take several minutes depending on your internet connection..."
    echo ""
    
    if docker-compose build; then
        print_success "Docker images built successfully!"
    else
        print_error "Failed to build Docker images!"
        exit 1
    fi
}

# Start services
start_services() {
    print_status "Starting all services..."
    echo "This will start the complete microservices stack..."
    echo ""
    
    if docker-compose up -d; then
        print_success "All services started successfully!"
    else
        print_error "Failed to start services!"
        exit 1
    fi
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to become healthy..."
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        attempt=$((attempt + 1))
        echo -n "."
        
        if curl -sf http://localhost/health >/dev/null 2>&1; then
            echo ""
            print_success "All services are healthy!"
            return 0
        fi
        
        sleep 5
    done
    
    echo ""
    print_warning "Services may still be starting. Check status with: docker-compose ps"
}

# Create admin user
create_admin_user() {
    print_status "Creating admin user..."
    
    echo ""
    echo "Let's create an admin user for the system:"
    read -p "Admin username [admin]: " admin_username
    admin_username=${admin_username:-admin}
    
    read -p "Admin email [admin@example.com]: " admin_email
    admin_email=${admin_email:-admin@example.com}
    
    read -p "Admin full name [System Administrator]: " admin_fullname
    admin_fullname=${admin_fullname:-"System Administrator"}
    
    read -s -p "Admin password: " admin_password
    echo
    
    # Create admin user via API
    local response
    response=$(curl -s -X POST http://localhost/api/register \
        -H "Content-Type: application/json" \
        -d "{
            \"username\": \"$admin_username\",
            \"email\": \"$admin_email\",
            \"password\": \"$admin_password\",
            \"full_name\": \"$admin_fullname\"
        }" 2>/dev/null)
    
    if echo "$response" | grep -q "successfully"; then
        print_success "Admin user created successfully!"
        
        # Login to get token and display it
        local login_response
        login_response=$(curl -s -X POST http://localhost/api/login \
            -H "Content-Type: application/json" \
            -d "{
                \"username\": \"$admin_username\",
                \"password\": \"$admin_password\"
            }" 2>/dev/null)
        
        if echo "$login_response" | grep -q "token"; then
            print_status "Admin login successful!"
            echo ""
            echo -e "${CYAN}Admin credentials:${NC}"
            echo "  Username: $admin_username"
            echo "  Email: $admin_email"
            echo "  Access: http://localhost"
        fi
    else
        print_warning "Failed to create admin user automatically."
        echo "You can create one manually later using the API."
    fi
}

# Display final information
show_completion_info() {
    echo ""
    echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                        SYSTEM INFORMATION                     ║${NC}"
    echo -e "${CYAN}╠════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║${NC} 🌐 Main Application:     http://localhost                    ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC} 📊 Health Check:        http://localhost/health             ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC} 📧 Email Testing:       http://localhost:8025 (MailHog)     ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC} 🗄️  Database Admin:      http://localhost:5050 (pgAdmin)     ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC} 🔴 Redis Commander:     http://localhost:8081               ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC} 📈 Monitoring:          http://localhost:3000 (Grafana)     ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Useful Commands:${NC}"
    echo "  make status          - Check service status"
    echo "  make logs            - View all service logs"
    echo "  make health          - Check service health"
    echo "  make down            - Stop all services"
    echo "  make restart         - Restart all services"
    echo ""
    echo -e "${YELLOW}Service Ports:${NC}"
    echo "  User Service:        5001"
    echo "  Project/Task:        5002"
    echo "  Comment Service:     5003"
    echo "  Attachment Service:  5004"
    echo "  Notification:        5005"
    echo "  Activity Log:        5006"
    echo "  Reporting:           5007"
    echo ""
    echo -e "${GREEN}Happy coding! 🚀${NC}"
}

# Main execution
main() {
    echo "Starting automated setup..."
    echo ""
    
    check_prerequisites
    setup_environment
    create_directories
    setup_nginx_config
    build_images
    start_services
    wait_for_services
    create_admin_user
    show_completion_info
    
    echo ""
    print_status "Setup completed! Run 'make help' to see available commands."
}

# Handle script interruption
trap 'echo -e "\n${RED}Setup interrupted!${NC}"; exit 1' INT TERM

# Check if running with bash
if [ -z "$BASH_VERSION" ]; then
    print_error "This script requires bash to run."
    exit 1
fi

# Run main function
main "$@"
