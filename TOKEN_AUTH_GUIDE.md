# JWT Authentication API Guide

This Django project uses JWT (JSON Web Token) authentication for API endpoints, providing secure, stateless authentication with token expiration.

## Available Endpoints

### 1. Register a New User
**Endpoint:** `POST /api/auth/register/`

**Request Body:**
```json
{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_id": 1,
    "username": "newuser",
    "email": "user@example.com"
}
```

### 2. Login (Get JWT Tokens)
**Endpoint:** `POST /api/auth/login/`

**Request Body:**
```json
{
    "username": "newuser",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_id": 1,
    "username": "newuser",
    "email": "user@example.com"
}
```

### 3. Refresh Access Token
**Endpoint:** `POST /api/auth/token/refresh/`

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 4. Verify Token
**Endpoint:** `POST /api/auth/token/verify/`

**Request Body:**
```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{}
```
*Returns 200 OK if token is valid, 401 Unauthorized if invalid*

### 5. Logout (Blacklist Refresh Token)
**Endpoint:** `POST /api/auth/logout/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
    "message": "Successfully logged out"
}
```

### 6. Test Authentication
**Endpoint:** `GET /api/auth/test/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Response:**
```json
{
    "message": "Hello, newuser!",
    "user_id": 1,
    "username": "newuser",
    "email": "user@example.com"
}
```

## Using JWT Authentication with Todo Endpoints

All todo endpoints require authentication. Include the access token in the Authorization header with the "Bearer" prefix:

### List/Create Todos
**Endpoint:** `GET/POST /api/todos/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

### Retrieve/Update/Delete Todo
**Endpoint:** `GET/PUT/DELETE /api/todos/<id>/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

## Example Usage with cURL

### Register:
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'
```

### Login:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

### Refresh Token:
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN_HERE"}'
```

### Get Todos (Authenticated):
```bash
curl -X GET http://localhost:8000/api/todos/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Create Todo (Authenticated):
```bash
curl -X POST http://localhost:8000/api/todos/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task", "description": "Task description", "completed": false}'
```

### Logout:
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN_HERE"}'
```

## Example Usage with Python requests

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api"

# Register a new user
response = requests.post(f"{BASE_URL}/auth/register/", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
})
data = response.json()
access_token = data['access']
refresh_token = data['refresh']
print(f"Access Token: {access_token}")
print(f"Refresh Token: {refresh_token}")

# Use access token for authenticated requests
headers = {"Authorization": f"Bearer {access_token}"}

# Get todos
response = requests.get(f"{BASE_URL}/todos/", headers=headers)
print(response.json())

# Create a todo
response = requests.post(f"{BASE_URL}/todos/", headers=headers, json={
    "title": "New Task",
    "description": "Task description",
    "completed": False
})
print(response.json())

# Refresh the access token when it expires
response = requests.post(f"{BASE_URL}/auth/token/refresh/", json={
    "refresh": refresh_token
})
new_data = response.json()
access_token = new_data['access']
refresh_token = new_data.get('refresh', refresh_token)  # New refresh token if rotation enabled

# Update headers with new token
headers = {"Authorization": f"Bearer {access_token}"}

# Logout (blacklist refresh token)
response = requests.post(f"{BASE_URL}/auth/logout/", 
    headers=headers,
    json={"refresh": refresh_token}
)
print(response.json())
```

## JWT Token Lifecycle

### Access Token
- **Lifetime:** 60 minutes
- **Purpose:** Used for authenticating API requests
- **Usage:** Include in Authorization header as `Bearer <access_token>`
- **When it expires:** Request a new one using the refresh token

### Refresh Token
- **Lifetime:** 7 days
- **Purpose:** Used to obtain new access tokens
- **Usage:** Send to `/api/auth/token/refresh/` endpoint
- **Rotation:** Enabled - you get a new refresh token each time you refresh
- **Blacklisting:** After rotation, old refresh tokens are blacklisted

## Configuration

The following settings have been configured in `core/settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework_simplejwt',
    # ...
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

## Security Notes

1. **Always use HTTPS in production** - JWT tokens should never be transmitted over unencrypted connections
2. **Token Expiration** - Access tokens expire after 60 minutes, refresh tokens after 7 days
3. **Token Storage** - Store tokens securely on the client side (e.g., httpOnly cookies or secure storage)
4. **Refresh Token Rotation** - Enabled for enhanced security - old refresh tokens are blacklisted after use
5. **Logout** - Always call the logout endpoint to blacklist the refresh token when the user logs out
6. **Token Verification** - Use the verify endpoint to check if a token is still valid
7. **Secret Key** - Ensure your Django SECRET_KEY is strong and kept secure - it's used to sign JWTs
