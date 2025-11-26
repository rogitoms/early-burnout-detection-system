from django.db import models
from django.conf import settings  # Add this import

class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')  # Change this line
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    burnout_score = models.FloatField(null=True, blank=True)
    burnout_level = models.CharField(max_length=20, null=True, blank=True)
    recommendation = models.TextField(null=True, blank=True)
    llm_recommendations = models.TextField(null=True, blank=True)
    detailed_analysis = models.TextField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-started_at']

class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('question', 'Question'),
        ('answer', 'Answer'),
        ('system', 'System'),
    ]
    
    session = models.ForeignKey('ChatSession', on_delete=models.CASCADE, related_name='messages')  # Use string reference
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    question_id = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['timestamp']