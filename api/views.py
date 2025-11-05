from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from todo.models import Todo
from .serializers import TodoSerializer
import sqlite3
from django.http import JsonResponse
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class TodoListCreateView(generics.ListCreateAPIView):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TodoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)
    

def sql_injection_view(request):
    # Connect to the database
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    # Get the 'name' parameter from the request
    name = request.GET.get('name', '')

    # WARNING: The following line is vulnerable to SQL injection
    query = f"SELECT * FROM todo_todo WHERE name = '{name}'"
    cursor.execute(query)

    # Fetch all results
    rows = cursor.fetchall()

    # Close the connection
    conn.close()

    # Return the results as JSON
    return JsonResponse({'results': rows})

# JWT Authentication Views
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer to include additional user information
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add extra responses
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['email'] = self.user.email
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login view that returns access and refresh tokens with user info
    """
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(APIView):
    """
    API endpoint for user registration that returns JWT tokens
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.pk,
            'username': user.username,
            'email': user.email
        }, status=status.HTTP_201_CREATED)

class LogoutView(APIView):
    """
    API endpoint for user logout that blacklists the refresh token
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class JWTTestView(APIView):
    """
    Test endpoint to verify JWT authentication is working
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {
            'message': f'Hello, {request.user.username}!',
            'user_id': request.user.id,
            'username': request.user.username,
            'email': request.user.email
        }
        return Response(content)



