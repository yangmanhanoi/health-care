from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import jwt
import datetime
import uuid

class AlwaysAuthenticatedUser:
    """A user that is always authenticated for testing purposes"""
    def __init__(self, id=1, username="test_doctor", roles=None):
        self.id = id
        self.username = username
        self.is_authenticated = True
        self.roles = roles or ["DOCTOR"]  # Default role

class NoAuthAuthentication(BaseAuthentication):
    """
    Authentication class that bypasses authentication for testing.
    Always returns a mock user and adds a JWT token to the request.
    """
    def authenticate(self, request):
        # Create a mock user with doctor role
        user = AlwaysAuthenticatedUser()

        # Generate a JWT token for the mock user
        token = self._generate_test_token(user.id, user.username, user.roles)

        # Add Authorization header with the token
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'

        # For backward compatibility, also add the X-User headers
        request.META['HTTP_X_USER_ID'] = str(user.id)
        request.META['HTTP_X_USER_ROLES'] = '["DOCTOR"]'

        # Also set attributes directly on the request
        request.user_id = user.id
        request.roles = user.roles

        return (user, None)

    def authenticate_header(self, request):
        return 'Bearer'

    def _generate_test_token(self, user_id=1, username="test_doctor", roles=None):
        """Generate a JWT token for testing that's compatible with djangorestframework-simplejwt"""
        roles = roles or ["DOCTOR"]

        # Current time and expiry time
        now = datetime.datetime.now(datetime.timezone.utc)
        token_lifetime = datetime.timedelta(hours=1)

        # Create the payload with the exact fields expected by djangorestframework-simplejwt
        payload = {
            # Standard claims
            'token_type': 'access',
            'exp': now + token_lifetime,
            'iat': now,
            'jti': str(uuid.uuid4()),  # Unique identifier for this token

            # User information
            'user_id': user_id,
            'username': username,
            'roles': roles,
        }

        # Sign the token with HS256 algorithm (default for djangorestframework-simplejwt)
        token = jwt.encode(payload, settings.SIMPLE_JWT['SIGNING_KEY'], algorithm='HS256')
        return token