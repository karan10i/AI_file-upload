"""
API views for chat with AI agent.
"""
import logging
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ChatMessage, Conversation
from .serializers import (
    ChatInputSerializer,
    ChatResponseSerializer,
    ChatMessageSerializer,
    ConversationSerializer,
    ConversationListSerializer
)
from .agent import AIAgent

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_agent(request):
    """
    POST /api/chat/
    
    Send a message to the AI agent and receive a response.
    
    Request body:
    {
        "message": "Your message here",
        "conversation_id": "optional-uuid"  // To continue an existing conversation
    }
    
    Response:
    {
        "response": "AI response",
        "conversation_id": "uuid",
        "user_message": {...},
        "assistant_message": {...}
    }
    """
    # Validate input
    serializer = ChatInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user_message = serializer.validated_data['message']
    conversation_id = serializer.validated_data.get('conversation_id')
    
    try:
        # Get or create conversation
        if conversation_id:
            try:
                conversation = Conversation.objects.get(
                    id=conversation_id,
                    user=request.user
                )
            except Conversation.DoesNotExist:
                return Response(
                    {"error": "Conversation not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Create new conversation with first few words as title
            title = user_message[:50] + "..." if len(user_message) > 50 else user_message
            conversation = Conversation.objects.create(
                user=request.user,
                title=title
            )
        
        # Save user message
        user_msg = ChatMessage.objects.create(
            user=request.user,
            role='user',
            content=user_message
        )
        
        # Get chat history (last 10 messages for context)
        chat_history = list(
            ChatMessage.objects.filter(user=request.user)
            .order_by('-timestamp')[:10]
            .values('role', 'content')
        )
        chat_history.reverse()  # Put in chronological order
        
        # Initialize AI agent and get response
        agent = AIAgent(request.user)
        ai_response = agent.chat_sync(user_message, chat_history[:-1])  # Exclude current message
        
        # Save AI response
        assistant_msg = ChatMessage.objects.create(
            user=request.user,
            role='assistant',
            content=ai_response
        )
        
        # Update conversation timestamp
        conversation.save()  # This updates updated_at
        
        logger.info(f"Chat completed for user {request.user.id}")
        
        return Response({
            'response': ai_response,
            'conversation_id': str(conversation.id),
            'user_message': ChatMessageSerializer(user_msg).data,
            'assistant_message': ChatMessageSerializer(assistant_msg).data
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only conversations belonging to the current user."""
        return Conversation.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get all messages in a conversation.
        """
        conversation = self.get_object()
        messages = ChatMessage.objects.filter(
            user=request.user
        ).order_by('timestamp')
        
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def clear_history(self, request):
        """
        Clear all chat history for the current user.
        """
        ChatMessage.objects.filter(user=request.user).delete()
        Conversation.objects.filter(user=request.user).delete()
        return Response({"message": "Chat history cleared"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_history(request):
    """
    GET /api/chat/history/
    
    Get the user's recent chat messages.
    """
    limit = request.query_params.get('limit', 50)
    try:
        limit = int(limit)
    except ValueError:
        limit = 50
    
    messages = ChatMessage.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:limit]
    
    serializer = ChatMessageSerializer(messages, many=True)
    return Response(serializer.data)
