# Workshop Platform Backend 🚀

 Django REST API backend for the Workshop Platform - a comprehensive system for managing technology workshops and course enrollments.

## 🏗️ Architecture

- **Framework**: Django 5.2 + Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Token-based authentication
- **Deployment**: AWS EC2 with Nginx + Gunicorn
- **CI/CD**: GitHub Actions

## ✨ Features

- 🔐 **User Authentication** - Registration, login, token-based auth
- 📚 **Workshop Management** - CRUD operations for workshops and categories
- 📝 **Enrollment System** - Free workshop enrollment with tracking
- ⭐ **Reviews & Ratings** - User feedback system
- 🔍 **Search & Filtering** - Advanced workshop discovery
- 👤 **User Profiles** - Extended user management
- 📊 **Analytics Ready** - Structured data for insights

## 🚀 Quick Start

### Local Development

1. **Setup Environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Database**
   ```bash
   python manage.py migrate
   python manage.py populate_db  # Load sample data
   python manage.py createsu     # Create superuser
   ```

3. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

4. **Access API**
   - API Root: http://127.0.0.1:8000/api/
   - Admin Panel: http://127.0.0.1:8000/admin/
   - API Documentation: http://127.0.0.1:8000/api/docs/

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout

### Workshops
- `GET /api/workshops/` - List workshops (with filtering)
- `GET /api/workshops/{slug}/` - Workshop details
- `GET /api/categories/` - List categories

### User Management
- `GET /api/user/profile/` - Get user profile
- `PUT /api/user/profile/` - Update profile
- `GET /api/user/enrollments/` - User's enrollments
- `POST /api/enrollments/` - Enroll in workshop
- `DELETE /api/enrollments/{id}/` - Cancel enrollment

### Advanced Features
- `GET /api/workshops/{slug}/reviews/` - Workshop reviews
- `POST /api/workshops/{slug}/reviews/` - Add review
- `GET /api/user/wishlist/` - User's wishlist
- `POST /api/wishlist/` - Add to wishlist

## 🛠️ Development

### Project Structure
```
backend/
├── api/                     # Main Django app
│   ├── models.py           # Database models
│   ├── views.py            # API views
│   ├── serializers.py      # Data serializers
│   ├── urls.py             # URL routing
│   └── management/         # Custom commands
├── backend/                # Django project settings
├── requirements.txt        # Python dependencies
└── manage.py              # Django management
```

### Environment Variables
Create `.env` file:
```bash
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

### Running Tests
```bash
python manage.py test
python manage.py check
```

### Database Commands
```bash
python manage.py makemigrations  # Create migrations
python manage.py migrate         # Apply migrations
python manage.py populate_db     # Load sample data
python manage.py shell          # Django shell
```

## 🚀 Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

### Quick Deploy to EC2
1. **Set up GitHub Secrets** (see DEPLOYMENT.md)
2. **Push to main branch** - automatic deployment via GitHub Actions
3. **Monitor deployment** - check Actions tab in GitHub

### Environment Setup
```bash
# Production environment variables
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:5432/db
ALLOWED_HOSTS=your-domain.com,your-ec2-ip
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

## 🔍 API Usage Examples

### Authentication Flow
```python
# Register user
POST /api/auth/register/
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password",
    "first_name": "John",
    "last_name": "Doe"
}

# Login
POST /api/auth/login/
{
    "username": "john_doe",
    "password": "secure_password"
}
# Returns: {"token": "your-auth-token"}

# Use token in headers
Authorization: Token your-auth-token
```

### Workshop Operations
```python
# List workshops with filtering
GET /api/workshops/?category=frontend&difficulty=beginner&search=react

# Get workshop details
GET /api/workshops/react-fundamentals/

# Enroll in workshop
POST /api/enrollments/
{
    "workshop": "react-fundamentals"
}
```

## 🧪 Testing

### Test Data
The `populate_db` command creates:
- 5 categories (Frontend, Backend, DevOps, etc.)
- 13 sample workshops across all categories
- Sample user accounts for testing

### Manual Testing
```bash
# Test API endpoints
curl http://127.0.0.1:8000/api/workshops/
curl http://127.0.0.1:8000/api/categories/

# Test with authentication
curl -H "Authorization: Token your-token" \
     http://127.0.0.1:8000/api/user/profile/
```

## 🔒 Security Features

- **CORS Protection** - Configured for frontend domains
- **Token Authentication** - Secure API access
- **Input Validation** - Django REST Framework serializers
- **SQL Injection Protection** - Django ORM
- **XSS Protection** - Automatic escaping
- **CSRF Protection** - For web forms

## 📊 Performance

- **Database Optimization** - Indexed fields, efficient queries
- **Pagination** - All list endpoints paginated
- **Caching Ready** - Redis integration possible
- **Static Files** - Whitenoise for production

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

- **Documentation**: See DEPLOYMENT.md for deployment help
- **Issues**: GitHub Issues for bug reports
- **API Docs**: Available at `/api/docs/` when running