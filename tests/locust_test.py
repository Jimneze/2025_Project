"""
Locust Load Testing Suite for Django Todo Application

This file contains comprehensive load testing scenarios for:
- JWT Authentication (register, login, logout, token refresh)
- Todo CRUD operations (via API)
- Web UI Todo operations
- SQL Injection endpoint
- 2FA operations

Usage:
    locust -f tests/locust_test.py --host=http://localhost:8000
    
"""

from locust import HttpUser, task, between, SequentialTaskSet
import random
import string
import json


def generate_random_string(length=8):
    """Generate a random string for unique usernames/emails"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


class AuthenticationTasks(SequentialTaskSet):
    """Sequential authentication flow: register -> login -> test auth -> logout"""
    
    def on_start(self):
        """Initialize user credentials"""
        self.username = f"user_{generate_random_string()}"
        self.password = "TestPass123!"
        self.email = f"{self.username}@test.com"
        self.access_token = None
        self.refresh_token = None
        
    @task
    def register_user(self):
        """Register a new user via API"""
        response = self.client.post(
            "/api/auth/register/",
            json={
                "username": self.username,
                "email": self.email,
                "password": self.password
            },
            name="API: Register User"
        )
        
        if response.status_code == 201:
            data = response.json()
            self.access_token = data.get('access')
            self.refresh_token = data.get('refresh')
        else:
            print(f"Registration failed: {response.status_code} - {response.text}")
    
    @task
    def login_user(self):
        """Login with credentials"""
        response = self.client.post(
            "/api/auth/login/",
            json={
                "username": self.username,
                "password": self.password
            },
            name="API: Login User"
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access')
            self.refresh_token = data.get('refresh')
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
    
    @task
    def test_auth(self):
        """Test authenticated endpoint"""
        if self.access_token:
            self.client.get(
                "/api/auth/test-auth/",
                headers={"Authorization": f"Bearer {self.access_token}"},
                name="API: Test Auth Endpoint"
            )
    
    @task
    def refresh_token(self):
        """Refresh JWT token"""
        if self.refresh_token:
            response = self.client.post(
                "/api/auth/token/refresh/",
                json={"refresh": self.refresh_token},
                name="API: Refresh Token"
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access')
    
    @task
    def verify_token(self):
        """Verify JWT token"""
        if self.access_token:
            self.client.post(
                "/api/auth/token/verify/",
                json={"token": self.access_token},
                name="API: Verify Token"
            )
    
    @task
    def logout_user(self):
        """Logout user by blacklisting refresh token"""
        if self.refresh_token and self.access_token:
            self.client.post(
                "/api/auth/logout/",
                json={"refresh": self.refresh_token},
                headers={"Authorization": f"Bearer {self.access_token}"},
                name="API: Logout User"
            )


class TodoAPICRUDTasks(SequentialTaskSet):
    """Sequential Todo CRUD operations via API"""
    
    def on_start(self):
        """Setup: Register and login to get access token"""
        self.username = f"user_{generate_random_string()}"
        self.password = "TestPass123!"
        self.email = f"{self.username}@test.com"
        self.access_token = None
        self.todo_ids = []
        
        # Register
        response = self.client.post(
            "/api/auth/register/",
            json={
                "username": self.username,
                "email": self.email,
                "password": self.password
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            self.access_token = data.get('access')
    
    def get_auth_headers(self):
        """Return authorization headers"""
        return {"Authorization": f"Bearer {self.access_token}"}
    
    @task
    def create_todo(self):
        """Create a new todo"""
        if not self.access_token:
            return
            
        response = self.client.post(
            "/api/todos/",
            json={
                "title": f"Todo {generate_random_string(5)}",
                "name": f"Name {generate_random_string(5)}",
                "description": "Test todo description",
                "completed": False
            },
            headers=self.get_auth_headers(),
            name="API: Create Todo"
        )
        
        if response.status_code == 201:
            data = response.json()
            self.todo_ids.append(data.get('id'))
    
    @task
    def list_todos(self):
        """List all todos"""
        if not self.access_token:
            return
            
        self.client.get(
            "/api/todos/",
            headers=self.get_auth_headers(),
            name="API: List Todos"
        )
    
    @task
    def retrieve_todo(self):
        """Retrieve a specific todo"""
        if not self.access_token or not self.todo_ids:
            return
            
        todo_id = random.choice(self.todo_ids)
        self.client.get(
            f"/api/todos/{todo_id}/",
            headers=self.get_auth_headers(),
            name="API: Retrieve Todo"
        )
    
    @task
    def update_todo(self):
        """Update a specific todo"""
        if not self.access_token or not self.todo_ids:
            return
            
        todo_id = random.choice(self.todo_ids)
        self.client.put(
            f"/api/todos/{todo_id}/",
            json={
                "title": f"Updated Todo {generate_random_string(5)}",
                "name": f"Updated Name {generate_random_string(5)}",
                "description": "Updated description",
                "completed": random.choice([True, False])
            },
            headers=self.get_auth_headers(),
            name="API: Update Todo"
        )
    
    @task
    def partial_update_todo(self):
        """Partially update a todo"""
        if not self.access_token or not self.todo_ids:
            return
            
        todo_id = random.choice(self.todo_ids)
        self.client.patch(
            f"/api/todos/{todo_id}/",
            json={"completed": True},
            headers=self.get_auth_headers(),
            name="API: Partial Update Todo"
        )
    
    @task
    def delete_todo(self):
        """Delete a todo"""
        if not self.access_token or not self.todo_ids:
            return
            
        todo_id = self.todo_ids.pop(random.randrange(len(self.todo_ids)))
        self.client.delete(
            f"/api/todos/{todo_id}/",
            headers=self.get_auth_headers(),
            name="API: Delete Todo"
        )


class WebUITodoTasks(SequentialTaskSet):
    """Web UI Todo operations (requires session authentication)"""
    
    def on_start(self):
        """Setup: Register and login via web forms"""
        self.username = f"user_{generate_random_string()}"
        self.password = "TestPass123!"
        self.email = f"{self.username}@test.com"
        
        # Get CSRF token
        response = self.client.get("/accounts/register/", name="Web: Get Register Page")
        self.csrf_token = self.extract_csrf_token(response)
        
        # Register
        if self.csrf_token:
            response = self.client.post(
                "/accounts/register/",
                data={
                    "username": self.username,
                    "email": self.email,
                    "password1": self.password,
                    "password2": self.password,
                    "csrfmiddlewaretoken": self.csrf_token
                },
                name="Web: Register User"
            )
        
        # Login
        response = self.client.get("/accounts/login/", name="Web: Get Login Page")
        self.csrf_token = self.extract_csrf_token(response)
        
        if self.csrf_token:
            self.client.post(
                "/accounts/login/",
                data={
                    "username": self.username,
                    "password": self.password,
                    "csrfmiddlewaretoken": self.csrf_token
                },
                name="Web: Login User"
            )
    
    def extract_csrf_token(self, response):
        """Extract CSRF token from response"""
        if response.status_code == 200:
            # Simple extraction - in production, use proper HTML parsing
            content = response.text
            if 'csrfmiddlewaretoken' in content:
                start = content.find('csrfmiddlewaretoken') + len('csrfmiddlewaretoken')
                start = content.find('value="', start) + 7
                end = content.find('"', start)
                return content[start:end]
        return None
    
    @task
    def view_todo_list(self):
        """View the todo list page"""
        self.client.get("/todo/", name="Web: View Todo List")
    
    @task
    def create_todo_form(self):
        """Create a todo via web form"""
        # Get create page
        response = self.client.get("/todo/create/", name="Web: Get Create Todo Page")
        csrf_token = self.extract_csrf_token(response)
        
        if csrf_token:
            self.client.post(
                "/todo/create/",
                data={
                    "title": f"Web Todo {generate_random_string(5)}",
                    "name": f"Web Name {generate_random_string(5)}",
                    "description": "Test description",
                    "csrfmiddlewaretoken": csrf_token
                },
                name="Web: Create Todo"
            )


class SQLInjectionTasks(SequentialTaskSet):
    """Test SQL Injection endpoint (for security testing)"""
    
    @task
    def normal_query(self):
        """Normal query to SQL injection endpoint"""
        name = f"test_{generate_random_string(5)}"
        self.client.get(
            f"/api/todos/sql-injection/?name={name}",
            name="SQL Injection: Normal Query"
        )
    
    @task
    def sql_injection_attempt(self):
        """SQL injection attempt (for testing only)"""
        injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE todo_todo; --",
            "' UNION SELECT NULL, NULL, NULL --",
            "admin'--",
            "' OR 1=1 --"
        ]
        
        payload = random.choice(injection_payloads)
        self.client.get(
            f"/api/todos/sql-injection/?name={payload}",
            name="SQL Injection: Attack Attempt"
        )


# User Classes - Different user behaviors

class APIUser(HttpUser):
    """User that primarily uses API endpoints"""
    wait_time = between(1, 3)
    weight = 3
    
    tasks = {
        AuthenticationTasks: 2,
        TodoAPICRUDTasks: 5,
        SQLInjectionTasks: 1
    }


class WebUser(HttpUser):
    """User that primarily uses web UI"""
    wait_time = between(2, 5)
    weight = 2
    
    tasks = [WebUITodoTasks]


class MixedUser(HttpUser):
    """User that uses both API and Web UI"""
    wait_time = between(1, 4)
    weight = 1
    
    @task(3)
    def api_tasks(self):
        """Execute API tasks"""
        task_set = TodoAPICRUDTasks(self)
        task_set.run()
    
    @task(1)
    def web_tasks(self):
        """Execute Web UI tasks"""
        task_set = WebUITodoTasks(self)
        task_set.run()


class SecurityTester(HttpUser):
    """User focused on security testing"""
    wait_time = between(1, 2)
    weight = 1
    
    tasks = [SQLInjectionTasks]
