from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify


def login_required(f):
    """Decorator to protect administrative HTML and JSON routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('dashboard.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

