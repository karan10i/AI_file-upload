"""
Serializers for document processing API.
"""
import os
from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for Document model with file validation.
    """
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'status', 'created_at', 'error_message']
        read_only_fields = ['id', 'status', 'created_at', 'error_message']
    
    def validate_file(self, value):
        """
        Validate file type and size.
        """
        # Check file extension
        allowed_extensions = ['.pdf', '.docx', '.txt']
        ext = os.path.splitext(value.name)[1].lower()
        
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported file type '{ext}'. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size ({value.size} bytes) exceeds maximum allowed size (50MB)"
            )
        
        return value
    
    def create(self, validated_data):
        """
        Create document instance with user from request.
        """
        # Auto-generate title from filename if not provided
        if not validated_data.get('title'):
            filename = validated_data['file'].name
            validated_data['title'] = os.path.splitext(filename)[0]
        
        # Set user from request context
        validated_data['user'] = self.context['request'].user
        
        return super().create(validated_data)


class DocumentListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for document list view.
    """
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'status', 'created_at']