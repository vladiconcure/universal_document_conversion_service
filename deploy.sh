#!/bin/bash
# Script to deploy the document converter service

set -e

echo "Document Converter Service Deployment"
echo "===================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    sudo usermod -aG docker $USER
    echo "Docker installed. You may need to log out and back in for group changes to take effect."
    echo "Please run this script again after logging back in."
    exit 0
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose installed."
fi

# Create data directories
mkdir -p ./data/uploads ./data/output
chmod -R 777 ./data

# Build and start the service
echo "Building and starting the document converter service..."
docker-compose up -d --build

echo "Waiting for service to start..."
sleep 10

# Check if the service is running
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "Service is running successfully!"
    echo "API is available at: http://localhost:8000"
    echo "You can test it by uploading a document to: http://localhost:8000/docs"
else
    echo "Service failed to start properly. Check logs with: docker-compose logs"
fi
