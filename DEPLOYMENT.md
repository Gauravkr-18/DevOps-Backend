# Workshop Platform Backend - EC2 Deployment

## 🚀 Deployment Architecture

This Django REST API backend is designed to deploy on AWS EC2 with the following components:

- **EC2 Instance**: Ubuntu server running Django with Gunicorn
- **Database**: PostgreSQL (RDS recommended for production)
- **Web Server**: Nginx reverse proxy
- **Process Manager**: Supervisor for Gunicorn
- **CI/CD**: GitHub Actions for automated deployment

## 📋 Prerequisites

### AWS Resources Required
- EC2 instance (t3.micro or larger)
- RDS PostgreSQL instance (optional, can use SQLite for testing)
- Security Group allowing HTTP (80), HTTPS (443), SSH (22)
- Elastic IP (recommended for consistent access)

### GitHub Secrets Required
```
EC2_HOST=your-ec2-public-ip
EC2_USERNAME=ubuntu
EC2_SSH_KEY=your-private-key-content
BACKEND_URL=https://your-backend-domain.com/api
SECRET_KEY=your-django-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/dbname
ALLOWED_HOSTS=your-domain.com,your-ec2-ip
```

## 🛠️ Manual Setup (First Time)

### 1. EC2 Server Setup
```bash
# Connect to your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python, Nginx, PostgreSQL client
sudo apt install python3.13 python3.13-venv python3-pip nginx postgresql-client git -y

# Create application directory
sudo mkdir -p /var/www/workshop-platform-backend
sudo chown ubuntu:ubuntu /var/www/workshop-platform-backend
```

### 2. Application Setup
```bash
cd /var/www/workshop-platform-backend

# Clone repository
git clone https://github.com/your-username/workshop-platform-backend.git .

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your production values

# Run migrations
cd backend
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsu  # Create superuser if needed
```

### 3. Nginx Configuration
```bash
sudo tee /etc/nginx/sites-available/workshop-backend << EOF
server {
    listen 80;
    server_name your-domain.com your-ec2-ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias /var/www/workshop-platform-backend/backend/staticfiles/;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/workshop-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Supervisor Configuration
```bash
sudo apt install supervisor -y

sudo tee /etc/supervisor/conf.d/workshop-backend.conf << EOF
[program:workshop-backend]
command=/var/www/workshop-platform-backend/venv/bin/gunicorn backend.wsgi:application
directory=/var/www/workshop-platform-backend/backend
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/workshop-backend.log
environment=PATH="/var/www/workshop-platform-backend/venv/bin"
EOF

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start workshop-backend
```

## 🔄 Automated Deployment

Once the manual setup is complete, GitHub Actions will handle deployments:

1. **Push to main branch** triggers deployment
2. **Tests run** (Django checks, migrations)
3. **Code deploys** to EC2 via SSH
4. **Services restart** automatically
5. **Health check** verifies deployment

## 🏗️ Environment Variables

Create `.env` file in backend directory:

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ec2-ip

# Database (use SQLite for testing, PostgreSQL for production)
DATABASE_URL=postgresql://username:password@host:5432/database_name
# or for SQLite: DATABASE_URL=sqlite:///db.sqlite3

# CORS Settings
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com,https://your-cloudfront-domain.cloudfront.net

# AWS S3 (if using for media files)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-media-bucket
```

## 🔍 Monitoring & Troubleshooting

### Check Application Status
```bash
# Check Gunicorn process
sudo supervisorctl status workshop-backend

# Check Nginx
sudo systemctl status nginx

# View logs
tail -f /var/log/workshop-backend.log
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Common Issues

1. **502 Bad Gateway**: Gunicorn not running
   ```bash
   sudo supervisorctl restart workshop-backend
   ```

2. **Database Connection Error**: Check DATABASE_URL
   ```bash
   cd /var/www/workshop-platform-backend/backend
   source ../venv/bin/activate
   python manage.py dbshell  # Test DB connection
   ```

3. **Static Files Not Loading**: Collect static files
   ```bash
   python manage.py collectstatic --noinput
   ```

## 🔒 SSL/HTTPS Setup (Optional)

For production, set up SSL with Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## 📊 Performance Optimization

1. **Database**: Use RDS PostgreSQL for production
2. **Caching**: Add Redis for session/cache storage
3. **Static Files**: Use CloudFront CDN
4. **Monitoring**: Set up CloudWatch or similar

## 🚨 Security Checklist

- [ ] Changed default SSH port
- [ ] Configured firewall (UFW)
- [ ] Set up fail2ban
- [ ] Regular security updates
- [ ] Database backup strategy
- [ ] Environment variables secured
- [ ] Debug mode disabled in production