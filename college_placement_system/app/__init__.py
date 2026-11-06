import os
from flask import Flask, render_template, jsonify
from app.extensions import db, migrate
from config import config_by_name, BASE_DIR


def create_app(config_name=None):
    """Flask Application Factory creating and configuring the app instance."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, 'app', 'templates'),
        static_folder=os.path.join(BASE_DIR, 'app', 'static')
    )

    # Load configuration
    cfg_class = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(cfg_class)
    
    # Resolve SQLALCHEMY_DATABASE_URI with smart fallback if MySQL is unreachable
    app.config['SQLALCHEMY_DATABASE_URI'] = _resolve_database_uri(app, cfg_class())

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints safely
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    return app


def _resolve_database_uri(app, cfg):
    """
    Resolve the database URI.
    If MySQL connection fails (e.g. invalid password or database not created yet),
    fall back gracefully to local SQLite so the application never crashes during demos.
    """
    db_uri = cfg.SQLALCHEMY_DATABASE_URI

    # If already an SQLite URI or running tests, return directly
    if 'sqlite' in db_uri.lower() or app.config.get('TESTING'):
        return db_uri

    try:
        from sqlalchemy import create_engine
        # Test the MySQL connection with a short timeout
        engine = create_engine(db_uri, connect_args={'connect_timeout': 3})
        with engine.connect() as conn:
            pass
        return db_uri
    except Exception as e:
        sqlite_path = os.path.join(BASE_DIR, cfg.SQLITE_DB_NAME)
        fallback_uri = f"sqlite:///{sqlite_path}"
        print("\n" + "="*70)
        print(" [DATABASE CONFIGURATION NOTICE]")
        print(f" MySQL Connection Failed: {e}")
        print(f" Seamlessly falling back to local database: {cfg.SQLITE_DB_NAME}")
        print(" To connect to your MySQL Server:")
        print("   1. Open .env (or copy from .env.example)")
        print("   2. Update DB_PASSWORD with your MySQL root password")
        print("   3. Ensure database 'college_placement_db' exists in MySQL")
        print("="*70 + "\n")
        return fallback_uri


def _register_blueprints(app):
    """Register application blueprints."""
    try:
        from app.routes.dashboard_routes import dashboard_bp
        app.register_blueprint(dashboard_bp)
    except ImportError:
        pass

    try:
        from app.routes.student_routes import student_bp
        app.register_blueprint(student_bp, url_prefix='/students')
    except ImportError:
        pass

    try:
        from app.routes.company_routes import company_bp
        app.register_blueprint(company_bp, url_prefix='/companies')
    except ImportError:
        pass

    try:
        from app.routes.placement_routes import placement_bp
        app.register_blueprint(placement_bp, url_prefix='/placements')
    except ImportError:
        pass

    try:
        from app.routes.eligibility_routes import eligibility_bp
        app.register_blueprint(eligibility_bp, url_prefix='/eligibility')
    except ImportError:
        pass

    try:
        from app.routes.analytics_routes import analytics_bp
        app.register_blueprint(analytics_bp, url_prefix='/analytics')
    except ImportError:
        pass

    try:
        from app.routes.prediction_routes import prediction_bp
        app.register_blueprint(prediction_bp, url_prefix='/prediction')
    except ImportError:
        pass

    try:
        from app.routes.api_routes import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
    except ImportError:
        pass


def _register_error_handlers(app):
    """Register custom error handlers for HTML and JSON API requests."""
    @app.errorhandler(400)
    def bad_request(error):
        if hasattr(error, 'description') and isinstance(error.description, dict):
            return jsonify(error.description), 400
        return jsonify({'error': 'Bad Request', 'message': str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        try:
            return render_template('errors/404.html'), 404
        except Exception:
            return jsonify({'error': 'Not Found', 'message': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        try:
            return render_template('errors/500.html'), 500
        except Exception:
            return jsonify({'error': 'Internal Server Error', 'message': str(error)}), 500
