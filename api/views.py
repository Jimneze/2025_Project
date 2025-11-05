from django.shortcuts import render
from rest_framework import generics, permissions
from todo.models import Todo
from .serializers import TodoSerializer
import sqlite3
from django.http import JsonResponse

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