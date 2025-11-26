# api/two_factor_serializers.py
from rest_framework import serializers
from django_otp import devices_for_user
from django_otp.plugins.otp_email.models import EmailDevice
from .models import CustomUser

class TwoFactorRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class TwoFactorVerifySerializer(serializers.Serializer):
    token = serializers.CharField(max_length=6, min_length=6)
    email = serializers.EmailField()

class Toggle2FASerializer(serializers.Serializer):
    enable = serializers.BooleanField()