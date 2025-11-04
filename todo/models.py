from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Todo(models.Model):
    title = models.CharField(max_length=200)
    name = models.CharField(max_length=100, help_text="Name associated with this todo")
    image = models.ImageField(upload_to='todo_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.name}"

    def get_absolute_url(self):
        return reverse('todo:todo_detail', kwargs={'pk': self.pk})
