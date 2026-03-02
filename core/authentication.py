from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom Authentication class that supports both standard Authorization headers 
    and HTTP-only cookies for JWT storage.
    """
    
    def authenticate(self, request):
        """
        Extracts and validates the JWT from either the 'Authorization' header 
        or the 'access_token' cookie.
        """
        header = self.get_header(request)
        raw_token = self.get_raw_token(header) if header else request.COOKIES.get('access_token')

        if not raw_token:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except Exception as e:
            print(f"!!! AUTH-ERORR: {e}")
            return None