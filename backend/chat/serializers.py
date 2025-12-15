"""
Serializers for chat API.
"""
from rest_framework import serializers
from .models import ChatMessage, Conversation


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for chat messages.
    """
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class ChatInputSerializer(serializers.Serializer):
    """
    Serializer for chat input.
    """
    message = serializers.CharField(max_length=10000)
    conversation_id = serializers.UUIDField(required=False, allow_null=True)


class ChatResponseSerializer(serializers.Serializer):
    """
    Serializer for chat response.
    """
    response = serializers.CharField()
    conversation_id = serializers.UUIDField()
    user_message = ChatMessageSerializer()
    assistant_message = ChatMessageSerializer()


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for conversations.
    """
    messages = ChatMessageSerializer(many=True, read_only=True, source='chatmessage_set')
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'message_count', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.chatmessage_set.count() if hasattr(obj, 'chatmessage_set') else 0


class ConversationListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for conversation list.
    """
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'message_count', 'last_message']
    
    def get_message_count(self, obj):
        return obj.chatmessage_set.count() if hasattr(obj, 'chatmessage_set') else 0
    
    def get_last_message(self, obj):
        last_msg = obj.chatmessage_set.last() if hasattr(obj, 'chatmessage_set') else None
        if last_msg:
            return {
                'role': last_msg.role,
                'content': last_msg.content[:100] + '...' if len(last_msg.content) > 100 else last_msg.content
            }
        return None
