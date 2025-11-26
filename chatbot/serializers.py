from rest_framework import serializers
from .models import ChatSession, ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'message_type', 'content', 'timestamp', 'question_id']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'user', 'started_at', 'completed_at', 'burnout_score', 
                 'burnout_level', 'recommendation','llm_recommendations', 'detailed_analysis', 'is_complete', 'messages']

class StartChatSessionSerializer(serializers.Serializer):
    pass

class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer = serializers.CharField(max_length=1000)