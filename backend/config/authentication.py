from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class QueryParamJWTAuthentication(JWTAuthentication):
    """Allows JWT to be passed as ?token= for browser-navigable endpoints like PDF downloads."""
    def authenticate(self, request):
        token = request.query_params.get('token')
        if not token:
            return super().authenticate(request)  # fall back to header
        try:
            validated = self.get_validated_token(self.get_raw_token(
                f"Bearer {token}".encode()
            ))
            return self.get_user(validated), validated
        except (InvalidToken, TokenError):
            return None