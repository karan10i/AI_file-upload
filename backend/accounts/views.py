from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserSerializer, AdminUserSerializer

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'User created successfully',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_profile(request):
    """Get current user profile"""
    if request.user.is_authenticated:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


# ============================================
# Admin API Endpoints
# ============================================

class AdminUserListView(APIView):
    """
    GET /api/admin/users - List all users (Admin only)
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        users = User.objects.all().order_by('-date_joined')
        serializer = AdminUserSerializer(users, many=True)
        return Response({
            'count': users.count(),
            'users': serializer.data
        })


class AdminBlockUserView(APIView):
    """
    PATCH /api/admin/users/:id/block - Block/Unblock a user (Admin only)
    Sets is_active=False to block, is_active=True to unblock
    """
    permission_classes = [IsAdminUser]
    
    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        
        # Prevent admin from blocking themselves
        if user.id == request.user.id:
            return Response(
                {'error': 'Cannot block yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Toggle or set is_active based on request body
        # If 'block' is provided in body, use it; otherwise toggle
        block_action = request.data.get('block', None)
        
        if block_action is not None:
            user.is_active = not block_action  # block=True means is_active=False
        else:
            user.is_active = not user.is_active  # Toggle
        
        user.save()
        
        action = 'blocked' if not user.is_active else 'unblocked'
        return Response({
            'message': f'User {user.email} has been {action}',
            'user': AdminUserSerializer(user).data
        })


class AdminAIUsageView(APIView):
    """
    GET /api/admin/ai-usage - Get AI usage statistics (Admin only)
    Returns count of ChatMessages and Tasks created by AI
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        from chat.models import ChatMessage
        from tasks.models import Task
        
        # Count total chat messages
        total_messages = ChatMessage.objects.count()
        
        # Count messages by role
        user_messages = ChatMessage.objects.filter(role='user').count()
        assistant_messages = ChatMessage.objects.filter(role='assistant').count()
        
        # Count tasks created by AI
        total_tasks = Task.objects.count()
        ai_created_tasks = Task.objects.filter(created_by_ai=True).count()
        user_created_tasks = Task.objects.filter(created_by_ai=False).count()
        
        # Get unique users who have used the AI
        unique_chat_users = ChatMessage.objects.values('user').distinct().count()
        
        return Response({
            'chat_statistics': {
                'total_messages': total_messages,
                'user_messages': user_messages,
                'assistant_messages': assistant_messages,
                'unique_users': unique_chat_users,
            },
            'task_statistics': {
                'total_tasks': total_tasks,
                'ai_created_tasks': ai_created_tasks,
                'user_created_tasks': user_created_tasks,
            },
            'summary': {
                'total_ai_interactions': assistant_messages,
                'total_ai_created_items': ai_created_tasks,
            }
        })
