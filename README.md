# RedCurtains Django Backend

A comprehensive Django REST API backend that **exactly matches** the functionality of the Spring Boot backend. This backend provides the same endpoints, data models, and features as the Kotlin/Spring Boot implementation.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### 1. Install Dependencies

```bash
# Install required packages
pip install django djangorestframework django-cors-headers djangorestframework-simplejwt mysqlclient

# Or install from requirements.txt (if available)
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE moviepoll;
```

### 3. Run Migrations

```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate
```

### 4. Start the Server

```bash
# Run the development server
python manage.py runserver 0.0.0.0:8000
```

### 5. Access the Application

- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

## 📊 Database Configuration

### MySQL Connection Details
- **Host**: localhost
- **Port**: 3306
- **Database**: moviepoll
- **Username**: root
- **Password**: MySqlDocker@2025

### Database Schema
The application uses Django ORM with automatic migrations. The schema includes:
- Enhanced User model with loyalty system
- Poll model with JSON-based options and votes
- Vote tracking system
- User profiles

## 🔧 API Endpoints

### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Refresh token
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/forgot/` - Forgot password (OTP)
- `POST /api/auth/verify-otp/` - Verify OTP
- `POST /api/auth/reset-password/` - Reset password

### User Management Endpoints
- `GET /api/users/` - Get all users
- `GET /api/users/{id}/` - Get user by ID
- `GET /api/users/email/{email}/` - Get user by email
- `POST /api/users/create/` - Create new user
- `PUT /api/users/{id}/update/` - Update user
- `POST /api/users/{id}/loyalty-points/` - Add loyalty points
- `POST /api/users/{id}/verify-email/` - Verify user email
- `POST /api/users/{id}/deactivate/` - Deactivate user
- `GET /api/users/loyalty-tier/{tier}/` - Get users by loyalty tier
- `GET /api/users/active/` - Get active users
- `GET /api/users/exists/{email}/` - Check if user exists
- `GET /api/users/health/` - Health check

### Poll Management Endpoints
- `GET /api/polls/` - Get all active polls
- `GET /api/polls/{id}/` - Get poll by ID
- `POST /api/polls/create/` - Create new poll
- `POST /api/polls/{id}/vote/` - Vote on poll
- `DELETE /api/polls/{id}/delete/` - Delete poll
- `GET /api/polls/category/{category}/` - Get polls by category
- `GET /api/polls/user/{userId}/` - Get polls by user
- `GET /api/polls/visibility/{visibility}/` - Get polls by visibility
- `GET /api/polls/{id}/statistics/` - Get poll statistics
- `GET /api/polls/categories/` - Get available categories
- `GET /api/polls/health/` - Health check

## 📝 Sample API Requests

### User Registration
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "firstName": "John",
    "lastName": "Doe"
  }'
```

### User Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "rememberMe": false
  }'
```

### Create Poll
```bash
curl -X POST http://localhost:8000/api/polls/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is your favorite movie genre?",
    "options": ["Action", "Comedy", "Drama", "Horror"],
    "category": "Entertainment",
    "isAnonymous": false,
    "visibility": "PUBLIC",
    "createdByUserId": 1
  }'
```

### Vote on Poll
```bash
curl -X POST http://localhost:8000/api/polls/1/vote/ \
  -H "Content-Type: application/json" \
  -d '{
    "option": "Action",
    "voterUserId": 1
  }'
```

### Add Loyalty Points
```bash
curl -X POST http://localhost:8000/api/users/1/loyalty-points/ \
  -H "Content-Type: application/json" \
  -d '{
    "points": 100
  }'
```

## 🏗️ Project Structure

```
core/
├── models.py              # Enhanced User and Poll models
├── serializers.py         # Comprehensive serializers
├── views.py              # All API endpoints
├── urls.py               # URL routing
├── admin.py              # Admin interface
└── migrations/           # Database migrations

moviepoll/
├── settings.py           # Enhanced Django settings
├── urls.py              # Main URL configuration
└── wsgi.py              # WSGI configuration
```

## 🔐 Security Features

- **Password Hashing**: Django's built-in password hashing
- **JWT Authentication**: Secure token-based authentication
- **CORS Configuration**: Proper cross-origin resource sharing
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Proper HTTP status codes and error messages
- **XSS Protection**: Browser XSS filter enabled
- **CSRF Protection**: Configurable CSRF protection

## 🎯 Features

### User Management
- User registration and authentication
- Email verification system
- User profile management
- Account deactivation
- Loyalty points system with automatic tier calculation
- Password reset via OTP

### Polling System
- Create polls with multiple options
- Vote tracking and statistics
- Poll categories and visibility settings
- User-created polls (not just admin)
- Real-time results display
- Poll management (edit, delete)

### Database Features
- Automatic schema generation
- Optimized indexes for performance
- JSON-based poll options and votes
- Proper relationships and constraints
- Migration support

## 🛠️ Development

### Running Tests
```bash
python manage.py test
```

### Creating Superuser
```bash
python manage.py createsuperuser
```

### Database Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Admin Interface
Access the Django admin at http://localhost:8000/admin to manage users, polls, and other data.

## 📦 Dependencies

- **Django**: 5.2.2 - Web framework
- **Django REST Framework**: API framework
- **Django CORS Headers**: CORS support
- **Django REST Framework SimpleJWT**: JWT authentication
- **MySQL Client**: MySQL database connector

## 🔍 API Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "errors": { ... }
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Ensure MySQL is running
   - Check database credentials in settings.py
   - Verify database exists

2. **Migration Errors**
   - Delete existing migrations: `rm core/migrations/0*.py`
   - Recreate migrations: `python manage.py makemigrations`
   - Apply migrations: `python manage.py migrate`

3. **Import Errors**
   - Install missing dependencies: `pip install -r requirements.txt`
   - Check Python path and virtual environment

4. **CORS Issues**
   - Verify CORS settings in settings.py
   - Check allowed origins and headers

## 📄 Comparison with Spring Boot Backend

This Django backend provides **100% feature parity** with the Spring Boot backend:

| Feature | Spring Boot | Django | Status |
|---------|-------------|--------|--------|
| User Management | ✅ | ✅ | Complete |
| Authentication | ✅ | ✅ | Complete |
| Poll System | ✅ | ✅ | Complete |
| Loyalty System | ✅ | ✅ | Complete |
| API Endpoints | ✅ | ✅ | Complete |
| Security | ✅ | ✅ | Complete |
| Database | ✅ | ✅ | Complete |

## 📄 Licensec

This project is part of the RedCurtains cinema application and matches the Spring Boot backend functionality exactly.