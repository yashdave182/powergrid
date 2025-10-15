#!/bin/bash

# POWERGRID ML System Deployment Script
# This script sets up the complete POWERGRID ML prediction system

set -e  # Exit on any error

echo "🚀 Starting POWERGRID ML System Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.8+ is installed
check_python() {
    print_status "Checking Python version..."
    python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    required_version="3.8"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        print_error "Python 3.8+ is required. Found: $python_version"
        exit 1
    fi
    print_status "Python $python_version detected ✓"
}

# Create virtual environment
setup_virtual_env() {
    print_status "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created ✓"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_status "Virtual environment activated ✓"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    print_status "Dependencies installed ✓"
}

# Create directory structure
create_directories() {
    print_status "Creating directory structure..."
    
    directories=(
        "models"
        "outputs"
        "data/raw"
        "data/processed"
        "data/uploads"
        "logs"
        "tests"
        "scripts"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        fi
    done
}

# Setup environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# POWERGRID ML System Configuration

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
API_KEY=your-secret-api-key-here

# Model Configuration
MODELS_PATH=./models/
DATA_PATH=./data/
OUTPUTS_PATH=./outputs/

# Database Configuration (optional)
DATABASE_URL=sqlite:///./powergrid.db

# Security
SECRET_KEY=your-secret-key-here-$(date +%s)
JWT_SECRET_KEY=your-jwt-secret-key-here-$(date +%s)

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/powergrid.log
MAX_LOG_SIZE=10485760  # 10MB
BACKUP_COUNT=5

# Model Training
TRAINING_BATCH_SIZE=32
VALIDATION_SPLIT=0.2
RANDOM_STATE=42

# Performance
MAX_WORKERS=4
REQUEST_TIMEOUT=30
CACHE_TTL=3600

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
EOF
        print_status "Environment file created ✓"
    else
        print_warning "Environment file already exists"
    fi
}

# Download sample data
download_sample_data() {
    print_status "Setting up sample data..."
    
    # Create sample project data
    cat > data/sample_projects.csv << EOF
project_type,budget,estimated_timeline,terrain_type,environmental_clearance_status,material_cost_ratio,labor_cost_ratio,regulatory_complexity_score,monsoon_impact_score,vendor_risk_score,demand_supply_impact,resource_availability_score,cost_escalation_risk,timeline_pressure_score,weather_impact_ratio,trained_manpower_availability,historical_delay_pattern,regional_delay_factor,seasonal_factor,technology_risk,project_complexity_score,critical_path_risk,vendor_performance_score,location,start_date
substation,50000000,365,plain,approved,0.65,0.35,0.7,0.6,0.4,0.5,0.8,0.3,0.6,0.4,0.7,0.2,0.3,0.5,0.2,0.6,0.4,0.7,"Delhi","2024-01-15"
overhead_line,30000000,240,hilly,pending,0.7,0.3,0.8,0.7,0.5,0.6,0.6,0.4,0.7,0.6,0.5,0.4,0.5,0.7,0.3,0.7,0.5,0.6,"Himachal Pradesh","2024-02-01"
underground_cable,75000000,450,urban,approved,0.6,0.4,0.9,0.4,0.6,0.7,0.7,0.5,0.8,0.3,0.8,0.3,0.4,0.4,0.4,0.8,0.6,0.8,"Mumbai","2024-01-30"
substation,45000000,300,coastal,approved,0.55,0.45,0.6,0.8,0.3,0.4,0.9,0.2,0.5,0.8,0.9,0.1,0.2,0.8,0.1,0.5,0.3,0.9,"Kerala","2024-03-01"
overhead_line,35000000,280,forest,pending,0.75,0.25,0.85,0.6,0.7,0.8,0.5,0.6,0.6,0.7,0.4,0.5,0.6,0.6,0.2,0.6,0.7,0.5,"Assam","2024-02-15"
EOF
    
    print_status "Sample data created ✓"
}

# Create systemd service files
create_systemd_services() {
    print_status "Creating systemd service files..."
    
    # API Service
    cat > powergrid-api.service << EOF
[Unit]
Description=POWERGRID ML API Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/uvicorn src.api.enhanced_main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Dashboard Service
    cat > powergrid-dashboard.service << EOF
[Unit]
Description=POWERGRID ML Dashboard Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    print_status "Systemd service files created ✓"
    print_warning "To install services, run: sudo cp *.service /etc/systemd/system/"
}

# Create startup script
create_startup_script() {
    print_status "Creating startup script..."
    
    cat > start_system.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting POWERGRID ML System..."

# Activate virtual environment
source venv/bin/activate

# Start API server in background
echo "Starting API server..."
nohup uvicorn src.api.enhanced_main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
API_PID=$!
echo "API server started with PID: $API_PID"

# Wait for API to start
sleep 5

# Start Dashboard
echo "Starting Dashboard..."
nohup streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0 > logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo "Dashboard started with PID: $DASHBOARD_PID"

# Save PIDs
echo $API_PID > logs/api.pid
echo $DASHBOARD_PID > logs/dashboard.pid

echo "✅ POWERGRID ML System started successfully!"
echo "📊 API Server: http://localhost:8000"
echo "📈 Dashboard: http://localhost:8501"
echo "📋 Logs available in: logs/"
EOF

    chmod +x start_system.sh
    print_status "Startup script created ✓"
}

# Create shutdown script
create_shutdown_script() {
    print_status "Creating shutdown script..."
    
    cat > stop_system.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping POWERGRID ML System..."

# Stop API server
if [ -f logs/api.pid ]; then
    API_PID=$(cat logs/api.pid)
    kill $API_PID 2>/dev/null
    echo "API server stopped ✓"
    rm logs/api.pid
fi

# Stop Dashboard
if [ -f logs/dashboard.pid ]; then
    DASHBOARD_PID=$(cat logs/dashboard.pid)
    kill $DASHBOARD_PID 2>/dev/null
    echo "Dashboard stopped ✓"
    rm logs/dashboard.pid
fi

echo "✅ POWERGRID ML System stopped successfully!"
EOF

    chmod +x stop_system.sh
    print_status "Shutdown script created ✓"
}

# Create requirements file
create_requirements() {
    print_status "Creating requirements.txt..."
    
    cat > requirements.txt << EOF
# Core ML Libraries
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
xgboost==1.7.6
lightgbm==4.0.0
catboost==1.2.0

# Deep Learning
tensorflow==2.13.0
torch==2.0.1

# API Framework
fastapi==0.103.0
uvicorn==0.23.2
pydantic==2.4.2

# Dashboard
streamlit==1.27.0
plotly==5.17.0
altair==5.1.2

# Data Processing
imbalanced-learn==0.11.0
 category_encoders==2.6.0
feature-engine==1.6.1

# Visualization
matplotlib==3.7.2
seaborn==0.12.2

# Utilities
python-multipart==0.0.6
aiofiles==23.2.1
python-dotenv==1.0.0
joblib==1.3.2
tqdm==4.66.1

# Monitoring
prometheus-client==0.17.1

# Development
pytest==7.4.2
pytest-asyncio==0.21.1
black==23.9.1
flake8==6.1.0
mypy==1.5.1

# Security
cryptography==41.0.4
passlib==1.7.4
python-jose==3.3.0

# Database
sqlalchemy==2.0.21
alembic==1.12.0

# Async Support
asyncio==3.4.3
aioredis==2.0.1
EOF

    print_status "Requirements file created ✓"
}

# Create Docker configuration
create_docker_config() {
    print_status "Creating Docker configuration..."
    
    # Dockerfile
    cat > Dockerfile << 'EOF'
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p models outputs data/uploads logs

# Expose ports
EXPOSE 8000 8501 9090

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["./start_system.sh"]
EOF

    # Docker Compose
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  powergrid-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - MODELS_PATH=/app/models/
      - DATA_PATH=/app/data/
    volumes:
      - ./models:/app/models
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  powergrid-dashboard:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    volumes:
      - ./models:/app/models
      - ./data:/app/data
      - ./outputs:/app/outputs
    restart: unless-stopped
    depends_on:
      - powergrid-api

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped

volumes:
  redis_data:
  prometheus_data:
EOF

    print_status "Docker configuration created ✓"
}

# Create monitoring configuration
create_monitoring_config() {
    print_status "Creating monitoring configuration..."
    
    # Prometheus configuration
    cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'powergrid-api'
    static_configs:
      - targets: ['powergrid-api:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
EOF

    print_status "Monitoring configuration created ✓"
}

# Main deployment function
main() {
    echo "🎯 POWERGRID ML System Deployment"
    echo "===================================="
    
    # Check Python version
    check_python
    
    # Setup virtual environment
    setup_virtual_env
    
    # Create directory structure
    create_directories
    
    # Setup environment variables
    setup_environment
    
    # Create requirements file
    create_requirements
    
    # Install dependencies
    install_dependencies
    
    # Download sample data
    download_sample_data
    
    # Create startup/shutdown scripts
    create_startup_script
    create_shutdown_script
    
    # Create systemd services
    create_systemd_services
    
    # Create Docker configuration
    create_docker_config
    
    # Create monitoring configuration
    create_monitoring_config
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Review and update .env file with your configuration"
    echo "2. Start the system: ./start_system.sh"
    echo "3. Access API: http://localhost:8000"
    echo "4. Access Dashboard: http://localhost:8501"
    echo "5. Check logs: tail -f logs/api.log"
    echo ""
    echo "📚 Documentation: POWERGRID_DOCUMENTATION.md"
    echo "🐳 Docker: docker-compose up -d"
    echo "🔄 Systemd: sudo cp *.service /etc/systemd/system/"
    echo ""
}

# Run main function
main "$@"