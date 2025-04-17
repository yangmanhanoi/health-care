from flask import Blueprint, request, jsonify
import requests
from middleware.auth import authenticate
from config import SERVICES
import json

router = Blueprint("router", __name__)

@router.route('/<service_prefix>/<path:path>', methods = ['POST', 'GET', 'PUT', 'DELETE'])
@authenticate()
def forward_to_service(service_prefix, path):
    user = request.user  # Đã xác thực xong, lấy thông tin user
    token = request.headers.get('Authorization')

    # Kiểm tra xem service_prefix có hợp lệ không
    service_url = SERVICES.get(service_prefix)
    if not service_url:
        return jsonify({"error": f"Service '{service_prefix}' not found"}), 404
    
    # Xây dựng headers để forward
    headers = {
        'Authorization': token,
        'X-User-Roles': json.dumps(user['roles']) ,
        'X-User-Id': str(user['user_id'])
    }

    # Lấy dữ liệu từ request
    data = request.json if request.method in ['POST', 'PUT'] else None

    # Forward request tới service tương ứng
    service_request_url = f"{service_url}/{path}"

    # Forward tùy theo phương thức HTTP (POST, GET, PUT, DELETE)
    if request.method == 'POST':
        response = requests.post(service_request_url, json=data, headers=headers)
    elif request.method == 'GET':
        response = requests.get(service_request_url, headers=headers, params=request.args)
    elif request.method == 'PUT':
        response = requests.put(service_request_url, json=data, headers=headers)
    elif request.method == 'DELETE':
        response = requests.delete(service_request_url, headers=headers)

    # Trả lại phản hồi từ service cho client
    return jsonify(response.json()), response.status_code
