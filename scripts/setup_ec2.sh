#!/bin/bash

# EC2 Setup Script for Workshop Platform Backend
# Run this script on your EC2 instance to set up the backend environment

set -e

echo "Starting EC2 setup for Workshop Platform Backend..."

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv git nginx supervisor

# Create application directory
sudo mkdir -p /home/ubuntu/workshop-platform-backend
sudo chown ubuntu:ubuntu /home/ubuntu/workshop-platform-backend

# Clone repository (you'll need to replace with your GitHub repo URL)
cd /home/ubuntu
git clone https://github.com/yourusername/workshop-platform-backend.git

# Set up Python virtual environment
cd workshop-platform-backend
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
cd backend
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Set up database (using PostgreSQL for production)
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres createuser --interactive --pwprompt workshop_user
sudo -u postgres createdb --owner=workshop_user workshop_db

# Run Django setup
python manage.py migrate
python manage.py collectstatic --noinput

# Create superuser (optional)
echo "Creating Django superuser..."
python manage.py createsuperuser --noinput --username admin --email admin@example.com || true

echo "Backend EC2 setup completed!"
echo "Next steps:"
echo "1. Configure GitHub secrets for backend deployment"
echo "2. Set up SSL certificate for backend domain"
echo "3. Configure CORS settings for S3 frontend"