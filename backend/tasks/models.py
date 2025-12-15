"""
Task model for task management system.
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Task(models.Model):
    """
    Task model for managing user tasks.
    Can be created manually by users or automatically by the AI agent.
    """
    
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # User who created/owns the task
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tasks'
    )
    
    # Flag to indicate if task was created by AI agent
    created_by_ai = models.BooleanField(default=False)
    
    # Link tasks to documents for context
    linked_documents = models.ManyToManyField(
        'documents.Document',
        blank=True,
        related_name='linked_tasks'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.status})"
