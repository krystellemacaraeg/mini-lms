"""
Health Check Routes
Simple endpoint to verify backend is running
"""

from flask import Blueprint, jsonify
from datetime import datetime

# create blueprint (route group)
bp = Blueprint('health', __name__, url_prefix='/api')
@bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    Returns: Server status and timestamp
    """
    return jsonify({
        'status': 'success',
        'message': 'Mini-LMS Backend is running',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200