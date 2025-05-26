from flask import Blueprint, request, jsonify
import requests
from middleware.auth import authenticate
from config import SERVICES
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

router = Blueprint("router", __name__)

@router.route('/<service_prefix>/<path:path>', methods = ['POST', 'GET', 'PUT', 'DELETE'])
@authenticate()
def forward_to_service(service_prefix, path):

    token = request.headers.get('Authorization')

    # Kiểm tra xem service_prefix có hợp lệ không
    service_url = SERVICES.get(service_prefix)
    if not service_url:
        return jsonify({"error": f"Service '{service_prefix}' not found"}), 404

    # Xây dựng headers để forward
    headers = {
        'Authorization': token
    }

    if hasattr(request, 'user'):
        user = request.user  # Đã xác thực xong, lấy thông tin user
        headers['X-User-Roles'] = json.dumps(user['roles'])
        headers['X-User-Id'] = str(user['user_id'])


    # Lấy dữ liệu từ request
    data = request.json if request.method in ['POST', 'PUT'] else None

    # Forward request tới service tương ứng
    # Handle trailing slash properly to avoid 301 redirects
    # if path and not path.endswith('/'):
    #     path = f"{path}/"
    service_request_url = f"{service_url}/{path}"

    # Log the request details
    logging.debug(f"Forwarding {request.method} request to: {service_request_url}")
    logging.debug(f"Headers: {headers}")
    logging.debug(f"Data: {data}")

    # Forward tùy theo phương thức HTTP (POST, GET, PUT, DELETE)
    try:
        if request.method == 'POST':
            response = requests.post(service_request_url, json=data, headers=headers, timeout=10)
        elif request.method == 'GET':
            response = requests.get(service_request_url, headers=headers, params=request.args, timeout=10)
        elif request.method == 'PUT':
            response = requests.put(service_request_url, json=data, headers=headers, timeout=10)
        elif request.method == 'DELETE':
            response = requests.delete(service_request_url, headers=headers, timeout=10)

        # Log the response details
        logging.debug(f"Response status: {response.status_code}")
        logging.debug(f"Response headers: {response.headers}")
        logging.debug(f"Response content: {response.text}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return jsonify({"error": "Service unavailable"}), 503

    # Trả lại phản hồi từ service cho client
    if response.content:
        try:
            # Try to parse as JSON
            return jsonify(response.json()), response.status_code
        except (ValueError, requests.exceptions.JSONDecodeError):
            # If not valid JSON, return the raw content
            return response.text, response.status_code
    else:
        return '', response.status_code
