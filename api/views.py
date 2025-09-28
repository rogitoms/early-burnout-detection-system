from django.shortcuts import render

# Create your views here.
# api/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .serializers import UserSerializer, LoginSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from .models import CustomUser
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_otp import login as otp_login
from django_otp.plugins.otp_email.models import EmailDevice
from django_otp.util import random_hex
from .two_factor_serializers import TwoFactorRequestSerializer, TwoFactorVerifySerializer, Toggle2FASerializer
from django_otp import devices_for_user

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    try:
        data = request.data
        if not data.get('email') or not data.get('password'):
            return Response({'message': 'Email and password are required!'}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=data['email']).exists():
            return Response({'message': 'Email already exists!'}, status=status.HTTP_409_CONFLICT)

        user = CustomUser.objects.create_user(
            email=data['email'],
            password=data['password']
        )
        
        # AUTO-ENABLE 2FA FOR NEW USERS
        user.enable_2fa()
        
        # Create email device but don't log in yet - require 2FA first
        device, created = EmailDevice.objects.get_or_create(
            user=user,
            defaults={
                'name': 'Email Device',
                'confirmed': True,
            }
        )
        
        # Don't log the user in automatically - they need to verify 2FA first
        return Response({
            'message': 'User created successfully! 2FA verification required to complete setup.',
            'user': {
                'id': user.id,
                'email': user.email
            },
            'requires_2fa': True
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    try:
        data = request.data
        user = CustomUser.objects.filter(email=data['email']).first()
        
        if user and user.check_password(data['password']):
            # Check if 2FA is enabled
            if user.is_2fa_enabled:
                # Return response indicating 2FA is required
                return Response(
                    {
                        "message": "2FA verification required.",
                        "requires_2fa": True,
                        "email": user.email
                    },
                    status=status.HTTP_200_OK
                )
            else:
                # Regular login without 2FA
                login(request, user)
                return Response({
                    "message": "Login successful!",
                    "user": {
                        "id": user.id,
                        "email": user.email
                    },
                    "requires_2fa": False
                }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid email or password!"}, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        
        logout(request)
        return Response({"message": "Logout successful!"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_test(request):
    try:
        return Response({
            "message": f"Hello {request.user.email}, you are logged in!",
            "user": {
                "id": request.user.id,
                "email": request.user.email
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    return Response({'csrfToken': get_token(request)}, status=status.HTTP_200_OK)

# Add a simple health check endpoint
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"message": "API is working!"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def two_factor_request(request):
    """Request 2FA verification code"""
    from django.core.mail import send_mail
    from django.utils.html import strip_tags
    import random
    
    serializer = TwoFactorRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    
    try:
        user = CustomUser.objects.get(email=email)
        
        # Check if 2FA is enabled for this user
        if not user.is_2fa_enabled:
            return Response(
                {"message": "2FA is not enabled for this account."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create or get email device
        device, created = EmailDevice.objects.get_or_create(
            user=user,
            defaults={
                'name': 'Email Device',
                'confirmed': True,
            }
        )
        
        # Generate and send token - MANUAL TOKEN GENERATION
        try:
            # MANUALLY generate a 6-digit token
            token = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            print(f"DEBUG: Manually generated token: {token}")
            print(f"DEBUG: Sending to: {email}")
            
            # Store the token in the device
            device.token = token
            device.t0 = 0  # Start time for TOTP (not really used for static tokens)
            device.step = 600  # 10 minute expiration
            device.save()
            
            # Send custom email
            subject = 'Your 2FA Verification Code - Burnout Detection System'
            html_message = f"""
            <html>
                <body>
                    <h3>Burnout Detection System</h3>
                    <p>Your two-factor authentication verification code is:</p>
                    <h2 style="font-size: 24px; letter-spacing: 5px; color: #2563eb;">{token}</h2>
                    <p>This code will expire in 10 minutes.</p>
                    <p>If you didn't request this code, please ignore this email.</p>
                    <br>
                    <p>Best regards,<br>Burnout Detection System Team</p>
                </body>
            </html>
            """
            plain_message = f"""
            Burnout Detection System
            
            Your two-factor authentication verification code is: {token}
            
            This code will expire in 10 minutes.
            
            If you didn't request this code, please ignore this email.
            
            Best regards,
            Burnout Detection System Team
            """
            
            send_mail(
                subject,
                plain_message,
                'meriesara0000@gmail.com',
                [email],
                html_message=html_message,
                fail_silently=False,
            )
            
            print(f"DEBUG: Email sent successfully to {email} with token: {token}")
            
            return Response(
                {"message": "2FA verification code sent to your email."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(f"DEBUG: Failed to send 2FA email: {str(e)}")
            return Response(
                {"message": f"Failed to send verification code. Please try again. Error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except CustomUser.DoesNotExist:
        # Return generic message for security
        return Response(
            {"message": "If the email exists and 2FA is enabled, a verification code has been sent."},
            status=status.HTTP_200_OK
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def two_factor_verify(request):
    """Verify 2FA code and establish session"""
    import time
    from django.utils import timezone
    from datetime import timedelta
    
    serializer = TwoFactorVerifySerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    token = serializer.validated_data['token']
    email = serializer.validated_data['email']
    
    print(f"DEBUG: 2FA verify attempt - Email: {email}, Token: {token}")
    
    try:
        user = CustomUser.objects.get(email=email)
        print(f"DEBUG: Found user: {user.email}, 2FA enabled: {user.is_2fa_enabled}")
        
        # Get the email device
        devices = devices_for_user(user)
        email_devices = [d for d in devices if isinstance(d, EmailDevice)]
        
        if not email_devices:
            print("DEBUG: No email devices found")
            return Response(
                {"message": "No 2FA device found. Please request a new code."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        device = email_devices[0]
        print(f"DEBUG: Found device, stored token: {getattr(device, 'token', 'None')}")
        
        # Check if token matches
        if hasattr(device, 'token') and device.token == token:
            print("DEBUG: Token matches! Logging in user...")
            
            # IMPORTANT: Use regular Django login first, then OTP login
            login(request, user)
            print(f"DEBUG: Regular login successful for {user.email}")
            
            # Then establish OTP login
            otp_login(request, device)
            print("DEBUG: OTP login successful")
            
            # Verify session is established
            print(f"DEBUG: Session key exists: {bool(request.session.session_key)}")
            print(f"DEBUG: User is authenticated: {request.user.is_authenticated}")
            print(f"DEBUG: User ID: {getattr(request.user, 'id', 'None')}")
            
            # Clear the used token
            device.token = None
            device.save()
            print("DEBUG: Token cleared from device")
            
            return Response(
                {
                    "message": "2FA verification successful.",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "is_2fa_enabled": user.is_2fa_enabled
                    }
                },
                status=status.HTTP_200_OK
            )
        else:
            print(f"DEBUG: Token mismatch. Expected: {getattr(device, 'token', 'None')}, Got: {token}")
            return Response(
                {"message": "Invalid verification code."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    except CustomUser.DoesNotExist:
        print(f"DEBUG: User not found for email: {email}")
        return Response(
            {"message": "Invalid verification code."},  # Generic message for security
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        print(f"DEBUG: Unexpected error in 2FA verify: {str(e)}")
        return Response(
            {"message": "An error occurred during verification."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_2fa(request):
    """Enable or disable 2FA for the current user"""
    serializer = Toggle2FASerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    enable = serializer.validated_data['enable']
    
    if enable:
        request.user.enable_2fa()
        message = "2FA has been enabled for your account."
    else:
        request.user.disable_2fa()
        message = "2FA has been disabled for your account."
    
    return Response({"message": message}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_2fa_status(request):
    """Check if 2FA is enabled for current user"""
    return Response(
        {"is_2fa_enabled": request.user.is_2fa_enabled},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_2fa(request):
    """Enable 2FA for the current user and create email device"""
    from django.core.mail import send_mail
    from django.utils.html import strip_tags
    
    try:
        user = request.user
        
        # Create email device
        device, created = EmailDevice.objects.get_or_create(
            user=user,
            defaults={
                'name': 'Email Device',
                'confirmed': True,
            }
        )
        
        # Enable 2FA
        user.is_2fa_enabled = True
        user.save()
        
        # Test sending a code with custom email
        try:
            token = device.generate_token()
            print(f"DEBUG: Setup 2FA token: {token}")
            
            subject = '2FA Setup Complete - Burnout Detection System'
            html_message = f"""
            <html>
                <body>
                    <h3>2FA Setup Complete</h3>
                    <p>Two-factor authentication has been enabled for your account.</p>
                    <p>Your test verification code is:</p>
                    <h2 style="font-size: 24px; letter-spacing: 5px; color: #2563eb;">{token}</h2>
                    <p>This code will expire in 10 minutes.</p>
                    <br>
                    <p>Best regards,<br>Burnout Detection System Team</p>
                </body>
            </html>
            """
            plain_message = f"""
            2FA Setup Complete
            
            Two-factor authentication has been enabled for your account.
            
            Your test verification code is: {token}
            
            This code will expire in 10 minutes.
            
            Best regards,
            Burnout Detection System Team
            """
            
            send_mail(
                subject,
                plain_message,
                'meriesara0000@gmail.com',
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return Response(
                {"message": "2FA has been enabled. A test code has been sent to your email."},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {"message": f"2FA enabled but failed to send test email: {str(e)}"},
                status=status.HTTP_200_OK
            )
        
    except Exception as e:
        return Response(
            {"message": f"Failed to setup 2FA: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get current user information"""
    try:
        print(f"DEBUG: get_current_user called")
        print(f"DEBUG: User authenticated: {request.user.is_authenticated}")
        print(f"DEBUG: User ID: {getattr(request.user, 'id', 'None')}")
        print(f"DEBUG: User email: {getattr(request.user, 'email', 'None')}")
        print(f"DEBUG: Session key: {request.session.session_key}")
        
        if not request.user.is_authenticated:
            return Response(
                {"message": "User not authenticated"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return Response({
            'id': request.user.id,
            'email': request.user.email,
            'is_2fa_enabled': request.user.is_2fa_enabled
            # Add any other user fields you need
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"DEBUG: Error in get_current_user: {str(e)}")
        return Response(
            {"message": f"Error fetching user data: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        # api/views.py
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    try:
        print("Password reset request data:", request.data)
        
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            # Always return success message for security (don't reveal if email exists)
            return Response(
                {"message": "If the email exists in our system, a password reset link has been sent."},
                status=status.HTTP_200_OK
            )
        else:
            print("Serializer errors:", serializer.errors)
            return Response(
                {"message": "Invalid email format."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        print("Error in password_reset_request:", str(e))
        return Response(
            {"message": "An error occurred. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    try:
        print("Password reset confirm data:", request.data)
        
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Password has been reset successfully. You can now login with your new password."},
                status=status.HTTP_200_OK
            )
        else:
            print("Serializer errors:", serializer.errors)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        print("Error in password_reset_confirm:", str(e))
        return Response(
            {"message": "An error occurred. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )