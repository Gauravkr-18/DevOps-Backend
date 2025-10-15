#!/bin/bash

# Health check script for Workshop Platform
# This script verifies that all components are working correctly

echo "🔍 Starting health checks for Workshop Platform..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a service is running
check_service() {
    if systemctl is-active --quiet $1; then
        echo -e "${GREEN}✅ $1 is running${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 is not running${NC}"
        return 1
    fi
}

# Function to check HTTP endpoint
check_http() {
    if curl -f -s $1 > /dev/null; then
        echo -e "${GREEN}✅ $1 is responding${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 is not responding${NC}"
        return 1
    fi
}

# Function to check database connection
check_database() {
    cd /home/ubuntu/workshop-platform/backend
    source ../venv/bin/activate
    
    if python manage.py check --database default > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Database connection is working${NC}"
        return 0
    else
        echo -e "${RED}❌ Database connection failed${NC}"
        return 1
    fi
}

# Check system services
echo -e "\n${YELLOW}Checking system services...${NC}"
check_service nginx
check_service postgresql
check_service supervisor

# Check application service
echo -e "\n${YELLOW}Checking application service...${NC}"
if supervisorctl status workshop-platform | grep -q RUNNING; then
    echo -e "${GREEN}✅ workshop-platform is running${NC}"
else
    echo -e "${RED}❌ workshop-platform is not running${NC}"
fi

# Check HTTP endpoints
echo -e "\n${YELLOW}Checking HTTP endpoints...${NC}"
check_http "http://localhost"
check_http "http://localhost/api/"
check_http "http://localhost/admin/"

# Check database
echo -e "\n${YELLOW}Checking database connection...${NC}"
check_database

# Check disk space
echo -e "\n${YELLOW}Checking disk space...${NC}"
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    echo -e "${GREEN}✅ Disk usage: ${DISK_USAGE}%${NC}"
else
    echo -e "${RED}⚠️  Warning: Disk usage: ${DISK_USAGE}%${NC}"
fi

# Check memory usage
echo -e "\n${YELLOW}Checking memory usage...${NC}"
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
echo -e "${GREEN}📊 Memory usage: ${MEMORY_USAGE}%${NC}"

# Check log files for recent errors
echo -e "\n${YELLOW}Checking for recent errors...${NC}"
if [ -f /var/log/workshop-platform.log ]; then
    ERROR_COUNT=$(grep -c "ERROR" /var/log/workshop-platform.log | tail -100 || echo "0")
    if [ $ERROR_COUNT -eq 0 ]; then
        echo -e "${GREEN}✅ No recent errors in application logs${NC}"
    else
        echo -e "${YELLOW}⚠️  Found ${ERROR_COUNT} errors in recent logs${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Application log file not found${NC}"
fi

echo -e "\n${GREEN}🎉 Health check completed!${NC}"