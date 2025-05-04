import jwt
from flask import request, jsonify
from config import AUTH_SERVICE_SECRET
from functools import wraps
WHITELIST_PATHS = [
    ('svc-auth', 'api/login'),
    ('POST', 'svc-auth/api/login'),
    ('svc-auth', 'register'),
    ('svc-auth', 'refresh-token'),
    ('svc-doctor', 'get-doctor-info'),
    ('GET', 'svc-doctor/api/schedule/availabilities/doctor/<int:pk>'),
    ('GET', 'svc-doctor/api/schedule/availabilities/doctor/<int:pk>/<str:date>'),
    ('GET', 'svc-doctor/api/schedule/availabilities/<int:pk>'),
    ('svc-appointment', 'get-appointment-info')
]
def is_whitelisted(method, path):
    for m, p in WHITELIST_PATHS:
        if method == m and path.startswith(p):
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
    