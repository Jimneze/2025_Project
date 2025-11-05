from django.urls import path

from api.views import *

urlpatterns = [
    # serving todo API endpoints through django models
    path('todos/', TodoListCreateView.as_view(), name='todo-list-create'),
    path('todos/<int:pk>/', TodoRetrieveUpdateDestroyView.as_view(), name='todo-retrieve-update-destroy'),
    
    # serving api with capability of sql injection
    path('todos/sql-injection/', sql_injection_view),
]