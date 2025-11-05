from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from api.views import *

urlpatterns = [
    # serving todo API endpoints through django models
    path('todos/', TodoListCreateView.as_view(), name='todo-list-create'),
    path('todos/<int:pk>/', TodoRetrieveUpdateDestroyView.as_view(), name='todo-retrieve-update-destroy'),
    
    # serving api with capability of sql injection
    path('todos/sql-injection/', sql_injection_view),
    
    # JWT authentication endpoints
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/register/', RegisterView.as_view(), name='api-register'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/logout/', LogoutView.as_view(), name='api-logout'),
    path('auth/test/', JWTTestView.as_view(), name='api-test-auth'),
]