from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.middleware.csrf import get_token
from django.http import JsonResponse
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
import time


from rest_framework.authentication import SessionAuthentication

class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # Generate a unique refresh token
            refresh = RefreshToken.for_user(user)

            # Optionally add more custom data to the tokens, like a unique identifier or timestamp
            unique_identifier = uuid.uuid4().hex  # A unique value for each login session
            timestamp = int(time.time())  # Current timestamp to ensure uniqueness

            # Create a unique access token by embedding additional data (e.g., unique identifier, timestamp)
            refresh['unique_identifier'] = unique_identifier
            refresh['timestamp'] = timestamp

            access_token = str(refresh.access_token)

            return Response(
                {
                    'access_token': access_token,
                    'refresh_token': str(refresh),
                }, status=status.HTTP_200_OK
            )
        
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

# class logoutView(APIView):
#     permission_classes=[IsAuthenticated]

#     def post(self, request):
#         logout(request)
#         return Response({"message": "User logged out successfully."}, status=status.HTTP_200_OK)


from rest_framework_simplejwt.tokens import RefreshToken

class logoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  # Invalida el refresh token
            logout(request)
            return Response({"message": "User logged out successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Failed to blacklist refresh token"}, status=status.HTTP_400_BAD_REQUEST)


# class logoutView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         # Optionally retrieve the refresh token from the request body
#         refresh_token = request.data.get('refresh_token')
        
#         # If you're using refresh token to logout, blacklist it (invalidate it)
#         if refresh_token:
#             try:
#                 token = RefreshToken(refresh_token)
#                 token.blacklist()  # Blacklist the refresh token to invalidate it
#             except Exception as e:
#                 return Response({"error": "Failed to blacklist refresh token"}, status=status.HTTP_400_BAD_REQUEST)

#         # Logout user on the server side
#         logout(request)
#         return Response({"message": "User logged out successfully."}, status=status.HTTP_200_OK)

# class logoutView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         # Optionally retrieve the refresh token from the request body
#         refresh_token = request.data.get('refresh_token')

#         # If you're not using blacklist, no need to invalidate the refresh token
#         if refresh_token:
#             # You can log out the user but not blacklist the refresh token
#             pass

#         # Logout user on the server side
#         logout(request)
#         return Response({"message": "User logged out successfully."}, status=status.HTTP_200_OK)