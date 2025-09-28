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
    path('2fa/setup/', views.setup_2fa, name='setup_2fa'),
    path('2fa/request/', views.two_factor_request, name='two_factor_request'),
    path('2fa/verify/', views.two_factor_verify, name='two_factor_verify'),
    path('2fa/toggle/', views.toggle_2fa, name='toggle_2fa'),
    path('2fa/status/', views.check_2fa_status, name='check_2fa_status'),
    path('user/', views.get_current_user, name='get_current_user'),  # Fixed: removed 'api/auth/'
]