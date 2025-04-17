import jwt
from flask import request, jsonify
from config import AUTH_SERVICE_SECRET

def authenticate():
    def wrapper(f):
        def decorated(*args, **kwargs):
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
    