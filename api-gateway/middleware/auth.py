import jwt
from flask import request, jsonify
from config import AUTH_SERVICE_SECRET
from functools import wraps
WHITELIST_PATHS = [
    # Auth service endpoints - no authentication required
    ('POST', 'svc-auth/api/login'),
    ('POST', 'svc-auth/api/register/customer'),
    ('POST', 'svc-auth/api/register/patient'),
    ('POST', 'svc-auth/api/register/doctor'),
    ('POST', 'svc-auth/api/refresh-token'),

    # Doctor service endpoints - public access
    ('GET', 'svc-doctor/api/schedule/availabilities/doctor'),
    ('GET', 'svc-doctor/api/info'),

    # Chatbot service endpoints - public access
    ('GET', 'svc-chatbot/'),
    ('GET', 'svc-chatbot/health'),
    ('POST', 'svc-chatbot/chat'),

    # Legacy entries (keeping for backward compatibility)
    ('svc-auth', 'api/login'),
    ('svc-auth', 'api/register'),
    ('svc-doctor', 'get-doctor-info'),
    ('svc-appointment', 'get-appointment-info'),
    ('svc-laboratory', 'api/testtypes'),
    ('svc-laboratory', 'api/')
]
def is_whitelisted(method, path):
    for entry in WHITELIST_PATHS:
        if len(entry) == 2:
            m, p = entry
            # Check for method-specific whitelist (e.g., ('POST', 'svc-auth/api/login'))
            if m in ['GET', 'POST', 'PUT', 'DELETE']:
                if method == m and path.startswith(p):
                    return True
            # Check for general path whitelist (e.g., ('svc-auth', 'api/login'))
            else:
                if path.startswith(f"{m}/{p}"):
                    return True
    return False

def authenticate():
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            service_prefix = kwargs.get('service_prefix')
            path = kwargs.get('path')
            full_path = f"{service_prefix}/{path}"

            if is_whitelisted(request.method, full_path):
                return f(*args, **kwargs)  # Bỏ qua xác thực

            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"error": "Unauthorized"}), 401
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, AUTH_SERVICE_SECRET, algorithms=["HS256"])
                request.user = payload  # Gán user info vào request
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            return f(*args, **kwargs)
        return decorated
    return wrapper
