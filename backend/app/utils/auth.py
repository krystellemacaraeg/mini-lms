"""
Authentication Utilities
Password hashing and JWT token management
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from flask import current_app
from functools import wraps
from flask import request, jsonify

def hash_password(password):
    """
    Hash a password using bcrypt
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password
    """
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """
    Verify a password against its hash
    
    Args:
        password (str): Plain text password
        hashed_password (str): Stored hash
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def generate_token(user_id, role):
    """
    Generate JWT authentication token
    
    Args:
        user_id (int): User's database ID
        role (str): User's role ('student' or 'instructor')
        
    Returns:
        str: JWT token
    """
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        'iat': datetime.utcnow()  # Issued at
    }
    
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token

def decode_token(token):
    """
    Decode and verify JWT token
    
    Args:
        token (str): JWT token
        
    Returns:
        dict: Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

def token_required(f):
    """
    Decorator to protect routes - requires valid JWT token
    
    Usage:
        @bp.route('/protected')
        @token_required
        def protected_route(current_user):
            return jsonify({'message': f'Hello {current_user["user_id"]}'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Format: "Bearer <token>"
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        # Decode token
        payload = decode_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Pass user info to the route
        return f(current_user=payload, *args, **kwargs)
    
    return decorated

def role_required(required_role):
    """
    Decorator to restrict routes by role
    
    Usage:
        @bp.route('/instructor-only')
        @token_required
        @role_required('instructor')
        def instructor_route(current_user):
            return jsonify({'message': 'Welcome instructor'})
    """
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if current_user['role'] != required_role:
                return jsonify({
                    'error': f'Access denied. {required_role.capitalize()} role required.'
                }), 403
            
            return f(current_user=current_user, *args, **kwargs)
        
        return decorated
    return decorator