"""
API views for task management.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer, TaskListSerializer

logger = logging.getLogger(__name__)


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for task CRUD operations with user isolation.
    
    Provides:
    - GET /tasks/ - List all tasks for current user
    - POST /tasks/ - Create a new task
    - GET /tasks/{id}/ - Get task details
    - PUT /tasks/{id}/ - Update task
    - PATCH /tasks/{id}/ - Partial update
    - DELETE /tasks/{id}/ - Delete task
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only tasks belonging to the current user.
        Ensures user isolation - users can only see their own tasks.
        """
        return Task.objects.filter(created_by=self.request.user)
    
    def get_serializer_class(self):
        """
        Use appropriate serializer based on action.
        """
        if self.action == 'list':
            return TaskListSerializer
        elif self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        """
        Automatically set created_by to current user.
        """
        serializer.save(created_by=self.request.user)
        logger.info(f"Task created: {serializer.instance.title} by user {self.request.user.id}")
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get all active (non-done) tasks for the current user.
        """
        active_tasks = self.get_queryset().exclude(status='done')
        serializer = TaskListSerializer(active_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Get tasks grouped by status.
        """
        queryset = self.get_queryset()
        
        result = {
            'todo': TaskListSerializer(queryset.filter(status='todo'), many=True).data,
            'in_progress': TaskListSerializer(queryset.filter(status='in_progress'), many=True).data,
            'done': TaskListSerializer(queryset.filter(status='done'), many=True).data,
        }
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def mark_done(self, request, pk=None):
        """
        Quick action to mark a task as done.
        """
        task = self.get_object()
        task.status = 'done'
        task.save()
        
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def ai_created(self, request):
        """
        Get all tasks created by the AI agent.
        """
        ai_tasks = self.get_queryset().filter(created_by_ai=True)
        serializer = TaskListSerializer(ai_tasks, many=True)
        return Response(serializer.data)
