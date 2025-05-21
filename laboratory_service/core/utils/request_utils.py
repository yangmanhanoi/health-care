import json
import jwt
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

def extract_user_info_from_headers(request):
    """
    Extract user ID and roles from JWT token in the Authorization header.

    Args:
        request: The HTTP request object

    Returns:
        tuple: (user_id, roles, error_response)
            - user_id: The ID of the authenticated user
            - roles: List of roles assigned to the user
            - error_response: Response object if there's an error, None otherwise
    """
    auth_header = request.headers.get('Authorization')

    # For backward compatibility, still check for X-User headers
    if not auth_header and request.headers.get("X-User-Id"):
        request_user_id = request.headers.get("X-User-Id")
        roles_raw = request.headers.get('X-User-Roles')

        try:
            roles = json.loads(roles_raw) if roles_raw else []
            request_user_id = int(request_user_id)
            return request_user_id, roles, None
        except (json.JSONDecodeError, ValueError):
            return None, None, Response(
                {"error": "Invalid user information in headers"},
                status=status.HTTP_403_FORBIDDEN
            )

    # Process JWT token
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, None, Response(
            {"message": "Missing or invalid Authorization header. Format should be 'Bearer <token>'"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    token = auth_header.split(' ')[1]

    try:
        # Decode the JWT token
        payload = jwt.decode(
            token,
            settings.SIMPLE_JWT['SIGNING_KEY'],
            algorithms=['HS256'],
            options={"verify_exp": True}  # Ensure token expiration is checked
        )

        # Extract user_id and roles from the payload
        user_id = payload.get('user_id')
        roles = payload.get('roles', [])

        if not user_id:
            return None, None, Response(
                {"message": "Invalid token: missing user_id"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return user_id, roles, None

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
    except Exception as e:
        return None, None, Response(
            {"message": f"Error processing token: {str(e)}"},
            status=status.HTTP_401_UNAUTHORIZED
        )
