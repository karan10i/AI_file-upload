# AI Workspace Backend

Django REST Framework backend with JWT authentication to replace Clerk authentication in the React frontend.

## Features

- **Custom User Model** with email as username field
- **Workspace System** - Every user belongs to a workspace
- **JWT Authentication** with access and refresh tokens
- **PostgreSQL Database** for production use
- **Redis** for future Celery tasks
- **ChromaDB** for vector storage
- **Swagger Documentation** at `/swagger/`

## Setup Instructions

### Option 1: Using Docker (Recommended)

1. **Start all services:**
```bash
docker-compose up --build
```

2. **Run migrations in container:**
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py setup_initial_data
```

### Option 2: Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Setup PostgreSQL locally and update .env file**

3. **Run migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py setup_initial_data
```

4. **Start server:**
```bash
python manage.py runserver
```

## API Endpoints

### Authentication Endpoints

- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user (returns JWT tokens)
- `POST /api/auth/refresh/` - Refresh access token
- `GET /api/auth/profile/` - Get current user profile

### Example Usage

#### Register User
```javascript
const response = await fetch('http://localhost:8000/api/auth/register/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    username: 'username',
    password: 'securepassword123',
    password_confirm: 'securepassword123',
    first_name: 'John',
    last_name: 'Doe'
  })
});
```

#### Login User
```javascript
const response = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'securepassword123'
  })
});

const data = await response.json();
// Store tokens
localStorage.setItem('access_token', data.access);
localStorage.setItem('refresh_token', data.refresh);
```

#### Make Authenticated Requests
```javascript
const response = await fetch('http://localhost:8000/api/auth/profile/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'Content-Type': 'application/json',
  }
});
```

## Default Admin Account

- **Email:** admin@almo.com
- **Password:** admin123

Access Django admin at: `http://localhost:8000/admin/`

## Services

- **Django Backend:** `http://localhost:8000`
- **PostgreSQL:** `localhost:5432`
- **Redis:** `localhost:6379`
- **ChromaDB:** `http://localhost:8001`
- **Swagger Docs:** `http://localhost:8000/swagger/`