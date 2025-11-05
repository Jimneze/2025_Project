from rest_framework import serializers
from todo.models import Todo

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['id', 'title', 'name', 'image', 'description', 'completed', 'created_at', 'updated_at', 'user']