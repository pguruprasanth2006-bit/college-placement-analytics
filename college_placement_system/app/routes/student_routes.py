from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.extensions import db
from app.auth import login_required
from app.models import Student, Department

student_bp = Blueprint('students', __name__)


@student_bp.route('/')
@login_required
def index():
    """List all students with search, filters (department, graduation year), and pagination."""
    search_query = request.args.get('q', '').strip()
    dept_filter = request.args.get('department_id', type=int)
    year_filter = request.args.get('graduation_year', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 15

    query = Student.query

    if search_query:
        query = query.filter(
            (Student.name.ilike(f'%{search_query}%')) |
            (Student.register_number.ilike(f'%{search_query}%')) |
            (Student.email.ilike(f'%{search_query}%'))
        )

    if dept_filter:
        query = query.filter(Student.department_id == dept_filter)

    if year_filter:
        query = query.filter(Student.graduation_year == year_filter)

    pagination = query.order_by(Student.register_number.asc()).paginate(page=page, per_page=per_page, error_out=False)
    students = pagination.items
    departments = Department.query.order_by(Department.department_name.asc()).all()

    # Get distinct graduation years for dropdown filter
    grad_years = [r[0] for r in db.session.query(Student.graduation_year).distinct().order_by(Student.graduation_year.desc()).all() if r[0]]
    if not grad_years:
        grad_years = [2026, 2025, 2024, 2023]

    return render_template(
        'students.html',
        students=students,
        pagination=pagination,
        departments=departments,
        grad_years=grad_years,
        search_query=search_query,
        selected_dept=dept_filter,
        selected_year=year_filter
    )


@student_bp.route('/<int:student_id>')
@login_required
def view(student_id):
    """View individual student profile, placements, predictions, and eligibilities."""
    student = db.session.get(Student, student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('students.index'))
    return render_template('student_detail.html', student=student)


@student_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new student with strict validation."""
    departments = Department.query.order_by(Department.department_name.asc()).all()

    if request.method == 'POST':
        reg_no = request.form.get('register_number', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        dept_id = request.form.get('department_id', type=int)
        cgpa = request.form.get('cgpa', type=float)
        arrears = request.form.get('arrears', 0, type=int)
        grad_year = request.form.get('graduation_year', type=int)
        aptitude = request.form.get('aptitude_score', 0, type=int)
        technical = request.form.get('technical_score', 0, type=int)
        comm = request.form.get('communication_score', 0, type=int)
        intern = request.form.get('internship_experience', 0, type=int)
        skills = request.form.get('skills', '').strip()

        # Validations
        errors = []
        if not reg_no:
            errors.append("Register number is required.")
        elif Student.query.filter_by(register_number=reg_no).first():
            errors.append(f"Student with register number '{reg_no}' already exists.")

        if not name:
            errors.append("Student name is required.")

        if not email:
            errors.append("Email address is required.")
        elif Student.query.filter_by(email=email).first():
            errors.append(f"Student with email '{email}' already exists.")

        if not dept_id or not db.session.get(Department, dept_id):
            errors.append("A valid academic department must be selected.")

        if cgpa is None or cgpa < 0.0 or cgpa > 10.0:
            errors.append("CGPA must be a valid number between 0.0 and 10.0.")

        if arrears < 0:
            errors.append("Arrears cannot be negative.")

        if not grad_year or grad_year < 2000 or grad_year > 2040:
            errors.append("Please enter a valid 4-digit graduation year.")

        for score, label in [(aptitude, "Aptitude"), (technical, "Technical"), (comm, "Communication")]:
            if score < 0 or score > 100:
                errors.append(f"{label} score must be between 0 and 100.")

        if intern < 0:
            errors.append("Internship experience cannot be negative.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('student_form.html', student=None, departments=departments, form_data=request.form)

        try:
            student = Student(
                register_number=reg_no,
                name=name,
                email=email,
                phone=phone,
                department_id=dept_id,
                cgpa=cgpa,
                arrears=arrears,
                graduation_year=grad_year,
                aptitude_score=aptitude,
                technical_score=technical,
                communication_score=comm,
                internship_experience=intern,
                skills=skills
            )
            db.session.add(student)
            db.session.commit()
            flash(f"Student '{name}' ({reg_no}) registered successfully!", 'success')
            return redirect(url_for('students.index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error saving student: {str(e)}", 'danger')

    return render_template('student_form.html', student=None, departments=departments, form_data={})


@student_bp.route('/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit(student_id):
    """Edit student details."""
    student = db.session.get(Student, student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('students.index'))

    departments = Department.query.order_by(Department.department_name.asc()).all()

    if request.method == 'POST':
        reg_no = request.form.get('register_number', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        dept_id = request.form.get('department_id', type=int)
        cgpa = request.form.get('cgpa', type=float)
        arrears = request.form.get('arrears', 0, type=int)
        grad_year = request.form.get('graduation_year', type=int)
        aptitude = request.form.get('aptitude_score', 0, type=int)
        technical = request.form.get('technical_score', 0, type=int)
        comm = request.form.get('communication_score', 0, type=int)
        intern = request.form.get('internship_experience', 0, type=int)
        skills = request.form.get('skills', '').strip()

        errors = []
        if not reg_no:
            errors.append("Register number is required.")
        else:
            existing = Student.query.filter_by(register_number=reg_no).first()
            if existing and existing.id != student.id:
                errors.append(f"Another student with register number '{reg_no}' already exists.")

        if not name:
            errors.append("Student name is required.")

        if not email:
            errors.append("Email address is required.")
        else:
            existing = Student.query.filter_by(email=email).first()
            if existing and existing.id != student.id:
                errors.append(f"Another student with email '{email}' already exists.")

        if not dept_id or not db.session.get(Department, dept_id):
            errors.append("A valid academic department must be selected.")

        if cgpa is None or cgpa < 0.0 or cgpa > 10.0:
            errors.append("CGPA must be a valid number between 0.0 and 10.0.")

        if arrears < 0:
            errors.append("Arrears cannot be negative.")

        if not grad_year or grad_year < 2000 or grad_year > 2040:
            errors.append("Please enter a valid 4-digit graduation year.")

        for score, label in [(aptitude, "Aptitude"), (technical, "Technical"), (comm, "Communication")]:
            if score < 0 or score > 100:
                errors.append(f"{label} score must be between 0 and 100.")

        if intern < 0:
            errors.append("Internship experience cannot be negative.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('student_form.html', student=student, departments=departments, form_data=request.form)

        try:
            student.register_number = reg_no
            student.name = name
            student.email = email
            student.phone = phone
            student.department_id = dept_id
            student.cgpa = cgpa
            student.arrears = arrears
            student.graduation_year = grad_year
            student.aptitude_score = aptitude
            student.technical_score = technical
            student.communication_score = comm
            student.internship_experience = intern
            student.skills = skills

            db.session.commit()
            flash(f"Student '{name}' updated successfully!", 'success')
            return redirect(url_for('students.index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating student: {str(e)}", 'danger')

    return render_template('student_form.html', student=student, departments=departments, form_data={})


@student_bp.route('/delete/<int:student_id>', methods=['POST'])
@login_required
def delete(student_id):
    """Delete a student record."""
    student = db.session.get(Student, student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('students.index'))

    try:
        name = student.name
        reg_no = student.register_number
        db.session.delete(student)
        db.session.commit()
        flash(f"Student '{name}' ({reg_no}) was deleted successfully.", 'info')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting student: {str(e)}", 'danger')

    return redirect(url_for('students.index'))
