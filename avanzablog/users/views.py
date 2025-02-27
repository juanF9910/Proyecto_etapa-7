from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
import time
from .serializers import RegisterSerializer, LoginSerializer

class RegisterView(APIView):
    """
    View to register a new user.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    View to log in a user and return JWT tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request, 
            username=serializer.validated_data['username'], 
            password=serializer.validated_data['password']
        )

        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        refresh['session_id'] = uuid.uuid4().hex  # Unique session identifier
        refresh['timestamp'] = int(time.time())  # Unix timestamp for tracking

        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }, status=status.HTTP_200_OK)

class logoutView(APIView):
    """
    View to log out a user and blacklist their refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()  # Invalidate the refresh token
            except Exception as e:
                return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)

        logout(request)
        return Response({"message": "User logged out successfully."}, status=status.HTTP_200_OK)
