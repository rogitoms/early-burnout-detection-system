from django.shortcuts import render

# Create your views here.
# api/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .serializers import UserSerializer, LoginSerializer
from .models import CustomUser
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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
        
        # Log the user in after signup
        login(request, user)
        return Response({
            'message': 'User created successfully!',
            'user': {
                'id': user.id,
                'email': user.email
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    try:
        serializer = LoginSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response({'message': 'Invalid data provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = serializer.validated_data['user']
        login(request, user)
        
        return Response({
            'message': 'Login successful!',
            'user': {
                'id': user.id,
                'email': user.email
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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