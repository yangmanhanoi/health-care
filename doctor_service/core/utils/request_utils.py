import json
from rest_framework.response import Response
from rest_framework import status

def extract_user_info_from_headers(request):
    request_user_id = request.headers.get("X-User-Id")
    roles_raw = request.headers.get('X-User-Roles')

    if not request_user_id:
        return None, None, Response(
            {"message": "Missing X-User-Id"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        roles = json.loads(roles_raw) if roles_raw else []
        request_user_id = int(request_user_id)
        return request_user_id, roles, None
    except json.JSONDecodeError:
        return None, None, Response(
            {"error": "Invalid roles format"},
            status=status.HTTP_403_FORBIDDEN
        )