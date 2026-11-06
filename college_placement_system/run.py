import os
import sys

# Ensure application package is discoverable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from seed_data import seed_database

env_mode = os.getenv('FLASK_ENV', 'development')
app = create_app(env_mode)

host = os.getenv('FLASK_RUN_HOST', '127.0.0.1')
port = int(os.getenv('FLASK_RUN_PORT', 5000))
debug = env_mode == 'development'


def main():
    """Initialize database and start development server."""
    with app.app_context():
        try:
            db.create_all()
            from app.models import Student
            if Student.query.count() == 0:
                print("Database is empty. Running initial seeding...")
                seed_database(app)
        except Exception as e:
            print(f"Database initialization note: {e}")

    print(f"Starting College Placement Analytics & Prediction System on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
