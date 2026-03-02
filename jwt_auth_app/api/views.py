from os import access
from tokenize import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from urllib import response
from .serializers import RegistrationSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import  RegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

class RegistrationView(APIView):
    """
    Endpoint for new user registration.
    Allows any user to create an account.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Validates registration data and creates a new user instance.
        Returns a success message or validation errors.
        """
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            data = {
                "detail": "User created successfully!"
            }
            return Response(data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Custom Login view that issues JWTs (Access & Refresh) via HTTP-only cookies.
    This enhances security by preventing client-side JavaScript from accessing tokens.
    """
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """
        Authenticates user credentials and sets tokens in secure cookies.
        """
        response = super().post(request, *args, **kwargs)        
        if response.status_code != status.HTTP_200_OK:
            return response

        refresh = response.data.get('refresh')
        access = response.data.get('access')

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user 

        custom_response = Response({
            "detail": "Login successfully!",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }, status=status.HTTP_200_OK)

        custom_response.set_cookie(
            key='access_token', 
            value=access, 
            httponly=True,
            secure=False,
            samesite='Lax',
            path='/'
        )
        custom_response.set_cookie(
            key='refresh_token', 
            value=refresh, 
            httponly=True,
            secure=False,
            samesite='Lax',
            path='/' 
        )
        return custom_response
    
class CookieTokenRefreshView(TokenRefreshView):
    """
    Endpoint to refresh the access token using the refresh token stored in cookies.
    """
    def post(self, request, *args, **kwargs):
        """
        Extracts refresh token from cookies and issues a new access token.
        """
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            response.set_cookie('access_token', response.data['access'], httponly=True, secure=False, samesite='Lax', path='/')
            if 'refresh' in response.data:
                response.set_cookie('refresh_token', response.data['refresh'], httponly=True, secure=False, samesite='Lax', path='/')
            response.data = { "detail": "Token refreshed"}

        return response
    
class LogoutView(APIView):
    """
    Endpoint to log out a user by blacklisting their refresh token and deleting cookies.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Invalidates the refresh token and deletes the authentication cookies.
        """
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            
            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response({"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."}, status=status.HTTP_200_OK)
            
            response.delete_cookie('access_token', samesite='Lax', path='/')
            response.delete_cookie('refresh_token', samesite='Lax', path='/')
            
            return response
        except (TokenError, AttributeError):
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
    
