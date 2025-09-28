# backend/api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('protected-test/', views.protected_test, name='protected_test'),
    path('health/', views.health_check, name='health_check'),
    path('csrf/', views.get_csrf_token, name='get_csrf_token'),  
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/', views.password_reset_confirm, name='password_reset_confirm'),
]