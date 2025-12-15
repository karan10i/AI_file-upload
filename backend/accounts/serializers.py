from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Workspace

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password_confirm', 'first_name', 'last_name')
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
        
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        
        # Create default workspace for user
        workspace = Workspace.objects.create(
            name=f"{validated_data['email']}'s Workspace",
            description="Default workspace"
        )
        
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            workspace=workspace
        )
        user.set_password(validated_data['password'])
        user.save()
        
        return user


class UserSerializer(serializers.ModelSerializer):
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'role', 'workspace_name')
        read_only_fields = ('id', 'role')


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Extended user serializer for admin endpoints.
    Includes additional fields like is_active, date_joined, etc.
    """
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 
            'role', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'workspace_name'
        )
        read_only_fields = fields