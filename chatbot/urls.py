from django.urls import path
from . import views

urlpatterns = [
    path('start-session/', views.start_chat_session, name='start_chat_session'),
    path('submit-answer/', views.submit_answer, name='submit_answer'),
    path('history/', views.get_chat_history, name='chat_history'),
    path('session/<int:session_id>/', views.get_session_detail, name='session_detail'),
    path('session/<int:session_id>/delete/', views.delete_session, name='delete_session'),
    path('analyze-burnout/', views.analyze_burnout_message, name='analyze_burnout'),
]