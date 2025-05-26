import jwt
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status

def extract_user_info_from_jwt(request):
    """
    Extract user information from JWT token in Authorization header
    """
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return None, None, Response(
            {"message": "Missing or invalid Authorization header"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    token = auth_header.split(' ')[1]

    try:
        # Decode the JWT token using the same secret key as API Gateway
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

        # Extract user information from the token payload
        user_id = payload.get('user_id')
        roles = payload.get('roles', [])

        if not user_id:
            return None, None, Response(
                {"message": "Invalid token: missing user_id"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return int(user_id), roles, None

    except jwt.ExpiredSignatureError:
        return None, None, Response(
            {"message": "Token has expired"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except jwt.InvalidTokenError:
        return None, None, Response(
            {"message": "Invalid token"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except (ValueError, TypeError) as e:
        return None, None, Response(
            {"message": f"Token processing error: {str(e)}"},
            status=status.HTTP_401_UNAUTHORIZED
        )

def extract_user_info_from_headers(request):
    """
    Legacy function for backward compatibility - now uses JWT tokens
    """
    return extract_user_info_from_jwt(request)
