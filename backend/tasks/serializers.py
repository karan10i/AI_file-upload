"""
Serializers for task management API.
"""
from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """
    Full serializer for Task model.
    """
    linked_documents = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'due_date', 'created_at', 'updated_at', 'created_by_ai',
            'linked_documents'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_ai']


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating tasks (used by AI agent and users).
    """
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'due_date', 'created_by_ai', 'linked_documents'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        """
        Create task with user from request context.
        """
        # Handle linked_documents separately (ManyToMany)
        linked_docs = validated_data.pop('linked_documents', [])
        
        # Set user from request context
        validated_data['created_by'] = self.context['request'].user
        
        task = Task.objects.create(**validated_data)
        
        # Add linked documents if any
        if linked_docs:
            task.linked_documents.set(linked_docs)
        
        return task


class TaskListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for task list view.
    """
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'status', 'priority', 'due_date', 'created_by_ai']
