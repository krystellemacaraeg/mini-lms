"""
Flask Application Factory
Creates and configures the Flask app instance
"""

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

# initialize SQLAlchemy (database ORM)
db = SQLAlchemy()

def create_app():
    """
    Application factory pattern
    Returns configured Flask app
    """

    # initialize Flask app
    app = Flask(__name__)

    # configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

    # database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "../lms.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # initialize extensions
    db.init_app(app)

    # enable CORS (allow frontend to make requests)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # register blueprints (API routes)
    from app.routes import health, database
    app.register_blueprint(health.bp)
    app.register_blueprint(database.bp)

    # create database tables
    with app.app_context():
        db.create_all()

    return app