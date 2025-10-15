#!/bin/bash

# Backend Deployment script for Workshop Platform
# This script handles the backend deployment process on EC2

set -e

echo "Starting backend deployment process..."

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Navigate to project directory
cd "$PROJECT_DIR"

echo "Pulling latest changes from GitHub..."
git pull origin main

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing/updating Python dependencies..."
cd backend
pip install -r requirements.txt

echo "Running database migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running tests..."
python manage.py test --verbosity=2

echo "Restarting services..."
sudo supervisorctl restart workshop-platform-backend
sudo systemctl reload nginx

echo "Checking service status..."
sudo supervisorctl status workshop-platform-backend
sudo systemctl status nginx --no-pager -l

echo "Backend deployment completed successfully!"

# Optional: Run health checks
echo "Running health checks..."
sleep 5

# Check if the application is responding
if curl -f http://localhost:8000/api/ > /dev/null 2>&1; then
    echo "✅ Backend API is responding"
else
    echo "❌ Backend API is not responding"
    exit 1
fi

echo "🎉 Backend health checks passed!"