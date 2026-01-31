"""
Application Entry Point
Runs the Flask development server
"""

from app import create_app

# create Flask app instance
app = create_app()

if __name__ == '__main__':
    # run development server
    print("Starting Mini-LMS Backend...")
    print("Health check: http://localhost:5000/api/health")
    print("=" * 50)

    app.run(
        host='0.0.0.0',  # accept connections from any IP
        port=5000,       # backend runs on port 5000
        debug=True       # auto-reload on code changes
    )