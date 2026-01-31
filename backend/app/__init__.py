"""
Flask Application Factory
Creates and configures the Flask app instance
"""

from flask import Flask
from flask_cors import CORS

def create_app():
    """
    Application factory pattern
    Returns configured Flask app
    """

    # initialize Flask app
    app = Flask(__name__)

    # configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

    # enable CORS (allow frontend to make requests)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # register blueprints (API routes)
    from app.routes import health
    app.register_blueprint(health.bp)

    return app