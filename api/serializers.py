# backend/api/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email') # Don't expose the password

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.', code='authorization')
        else:
            raise serializers.ValidationError('Must include "email" and "password".', code='authorization')

        data['user'] = user
        return data

# api/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Check if email exists in the database
        if not User.objects.filter(email=value).exists():
            # Don't raise error here - return success message regardless for security
            return value
        return value

    def save(self):
        email = self.validated_data['email']
        
        # Check if user exists before proceeding
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # If user doesn't exist, we still return success for security reasons
            return
            
        # Generate token and UID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Build reset URL - update with your frontend URL
        reset_url = f"http://localhost:5173/password-reset-confirm/{uid}/{token}/"
        
        # Send email
        subject = "Password Reset Request - Burnout Detection System"
        message = f"""
        Hello,

        You requested a password reset for your Burnout Detection System account.

        Click the link below to reset your password:
        {reset_url}

        This link will expire in 1 hour.

        If you didn't request this password reset, please ignore this email.
        Your account security is important to us.

        Best regards,
        Burnout Detection System Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            print(f"Password reset email sent to: {email}")
        except Exception as e:
            print(f"Failed to send email to {email}: {str(e)}")

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Check if passwords match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        
        try:
            # Decode the uid
            from django.utils.encoding import force_str
            from django.utils.http import urlsafe_base64_decode
            
            uid = force_str(urlsafe_base64_decode(data['uid']))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"token": "Invalid reset link."})
        
        # Check if token is valid
        if not default_token_generator.check_token(self.user, data['token']):
            raise serializers.ValidationError({"token": "Invalid or expired reset link."})
        
        return data

    def save(self):
        new_password = self.validated_data['new_password']
        self.user.set_password(new_password)
        self.user.save()
        print(f"Password reset successfully for user: {self.user.email}")