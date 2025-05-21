#!/usr/bin/env python
"""
Script to generate JWT tokens for testing the prescription service.
This script creates a token with the specified user ID, username, and roles.

Usage:
    python generate_token.py --user_id 1 --username test_doctor --role DOCTOR

Roles can be one of: DOCTOR, PATIENT, ADMIN, PHARMACIST
"""

import jwt
import datetime
import uuid
import argparse
import os
import sys
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Import Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prescription_service.settings')
import django
django.setup()
from django.conf import settings

def generate_test_token(user_id=1, username="test_doctor", roles=None):
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate JWT tokens for testing')
    parser.add_argument('--role', choices=['DOCTOR', 'PATIENT', 'ADMIN', 'PHARMACIST'], default='DOCTOR',
                        help='Role to include in the token')
    parser.add_argument('--user_id', type=int, default=1, help='User ID to include in the token')
    parser.add_argument('--username', default='test_user', help='Username to include in the token')
    
    args = parser.parse_args()
    
    token = generate_test_token(
        user_id=args.user_id,
        username=args.username,
        roles=[args.role]
    )
    
    print(f"\nToken for {args.username} (ID: {args.user_id}, Role: {args.role}):")
    print(f"\n{token}\n")
    
    print("Use this token in your API requests with the header:")
    print(f'Authorization: Bearer {token}\n')
