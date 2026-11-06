from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.auth import login_required
from app.models import Student, Company, Placement, Department, AdminUser

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page and authentication handler."""
    if session.get('admin_logged_in'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Check against database AdminUser or configuration fallback
        admin_user = AdminUser.query.filter_by(username=username).first()
        valid = False

        if admin_user and admin_user.check_password(password):
            valid = True
        elif username == current_app.config.get('ADMIN_USERNAME') and password == current_app.config.get('ADMIN_PASSWORD'):
            valid = True

        if valid:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash(f'Welcome back, {username}!', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('dashboard.index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')


@dashboard_bp.route('/logout')
def logout():
    """Log out admin and clear session."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('dashboard.login'))


@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard showing KPI statistics, charts data, and recent placements."""
    total_students = Student.query.count()
    placed_students = Student.query.filter(Student.placements.any(status='Selected')).count()
    unplaced_students = max(0, total_students - placed_students)
    placement_percentage = round((placed_students / total_students * 100), 2) if total_students > 0 else 0.0

    companies_visited = Company.query.count()

    selected_placements = Placement.query.filter_by(status='Selected').all()
    if selected_placements:
        salaries = [p.salary for p in selected_placements if p.salary > 0]
        avg_package = round(sum(salaries) / len(salaries), 2) if salaries else 0.0
        max_package = round(max(salaries), 2) if salaries else 0.0
    else:
        avg_package = 0.0
        max_package = 0.0

    recent_placements = Placement.query.order_by(Placement.id.desc()).limit(8).all()

    # Department-wise statistics for chart
    departments = Department.query.all()
    dept_labels = []
    dept_placed_counts = []
    dept_total_counts = []

    for dept in departments:
        dept_labels.append(dept.department_code)
        t_count = dept.students.count()
        p_count = dept.students.filter(Student.placements.any(status='Selected')).count()
        dept_total_counts.append(t_count)
        dept_placed_counts.append(p_count)

    # Year-wise statistics for chart
    years = [2023, 2024, 2025, 2026]
    year_labels = [str(y) for y in years]
    year_placed_counts = []
    for y in years:
        p_y = Student.query.filter_by(graduation_year=y).filter(Student.placements.any(status='Selected')).count()
        year_placed_counts.append(p_y)

    return render_template(
        'dashboard.html',
        total_students=total_students,
        placed_students=placed_students,
        unplaced_students=unplaced_students,
        placement_percentage=placement_percentage,
        companies_visited=companies_visited,
        avg_package=avg_package,
        max_package=max_package,
        recent_placements=recent_placements,
        dept_labels=dept_labels,
        dept_placed_counts=dept_placed_counts,
        dept_total_counts=dept_total_counts,
        year_labels=year_labels,
        year_placed_counts=year_placed_counts
    )

