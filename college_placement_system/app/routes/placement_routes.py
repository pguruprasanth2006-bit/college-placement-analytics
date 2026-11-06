from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import func
from app.extensions import db
from app.auth import login_required
from app.models import Placement, Student, Company

placement_bp = Blueprint('placements', __name__)


@placement_bp.route('/')
@login_required
def index():
    """List all placements, filter by company or status, and display recruitment stats."""
    status_filter = request.args.get('status', '').strip()
    company_filter = request.args.get('company_id', type=int)

    query = Placement.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    if company_filter:
        query = query.filter_by(company_id=company_filter)

    placements = query.order_by(Placement.id.desc()).all()
    companies = Company.query.order_by(Company.company_name.asc()).all()

    # Company-wise recruitment statistics (counts of 'Selected' students)
    company_stats = (
        db.session.query(
            Company.company_name,
            func.count(Placement.id).label('total_placed'),
            func.avg(Placement.salary).label('avg_salary')
        )
        .join(Placement, Company.id == Placement.company_id)
        .filter(Placement.status == 'Selected')
        .group_by(Company.company_name)
        .order_by(func.count(Placement.id).desc())
        .all()
    )

    statuses = ['Applied', 'Shortlisted', 'Selected', 'Rejected', 'Not Placed']

    return render_template(
        'placements.html',
        placements=placements,
        companies=companies,
        company_stats=company_stats,
        statuses=statuses,
        selected_status=status_filter,
        selected_company=company_filter
    )


@placement_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Record student placement outcome or interview status."""
    students = Student.query.order_by(Student.register_number.asc()).all()
    companies = Company.query.order_by(Company.company_name.asc()).all()
    statuses = ['Applied', 'Shortlisted', 'Selected', 'Rejected', 'Not Placed']

    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        company_id = request.form.get('company_id', type=int)
        status = request.form.get('status', 'Applied').strip()
        salary = request.form.get('salary', 0.0, type=float)
        placement_date_str = request.form.get('placement_date', '').strip()

        errors = []
        if not student_id or not db.session.get(Student, student_id):
            errors.append("Please select a valid student.")
        if not company_id or not db.session.get(Company, company_id):
            errors.append("Please select a valid company.")
        if status not in statuses:
            errors.append("Invalid placement status.")

        # Check duplicate
        if student_id and company_id:
            existing = Placement.query.filter_by(student_id=student_id, company_id=company_id).first()
            if existing:
                errors.append("A placement record already exists for this student and company. Please edit the existing record.")

        placement_date = None
        if placement_date_str:
            try:
                placement_date = datetime.strptime(placement_date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append("Invalid date format. Use YYYY-MM-DD.")
        elif status == 'Selected':
            placement_date = date.today()

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('placement_form.html', placement=None, students=students, companies=companies, statuses=statuses, form_data=request.form)

        try:
            placement = Placement(
                student_id=student_id,
                company_id=company_id,
                status=status,
                salary=salary if salary else 0.0,
                placement_date=placement_date
            )
            db.session.add(placement)
            db.session.commit()
            flash("Placement record created successfully!", 'success')
            return redirect(url_for('placements.index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating placement: {str(e)}", 'danger')

    return render_template('placement_form.html', placement=None, students=students, companies=companies, statuses=statuses, form_data={})


@placement_bp.route('/edit/<int:placement_id>', methods=['GET', 'POST'])
@login_required
def edit(placement_id):
    """Edit placement details or update status."""
    placement = db.session.get(Placement, placement_id)
    if not placement:
        flash('Placement record not found.', 'danger')
        return redirect(url_for('placements.index'))

    students = Student.query.order_by(Student.register_number.asc()).all()
    companies = Company.query.order_by(Company.company_name.asc()).all()
    statuses = ['Applied', 'Shortlisted', 'Selected', 'Rejected', 'Not Placed']

    if request.method == 'POST':
        status = request.form.get('status', 'Applied').strip()
        salary = request.form.get('salary', 0.0, type=float)
        placement_date_str = request.form.get('placement_date', '').strip()

        errors = []
        if status not in statuses:
            errors.append("Invalid placement status.")

        placement_date = placement.placement_date
        if placement_date_str:
            try:
                placement_date = datetime.strptime(placement_date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append("Invalid date format. Use YYYY-MM-DD.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('placement_form.html', placement=placement, students=students, companies=companies, statuses=statuses, form_data=request.form)

        try:
            placement.status = status
            placement.salary = salary if salary else 0.0
            placement.placement_date = placement_date
            db.session.commit()
            flash("Placement record updated successfully!", 'success')
            return redirect(url_for('placements.index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating placement: {str(e)}", 'danger')

    return render_template('placement_form.html', placement=placement, students=students, companies=companies, statuses=statuses, form_data={})


@placement_bp.route('/delete/<int:placement_id>', methods=['POST'])
@login_required
def delete(placement_id):
    """Delete a placement record."""
    placement = db.session.get(Placement, placement_id)
    if not placement:
        flash('Placement record not found.', 'danger')
        return redirect(url_for('placements.index'))

    try:
        db.session.delete(placement)
        db.session.commit()
        flash('Placement record deleted successfully.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting placement: {str(e)}", 'danger')

    return redirect(url_for('placements.index'))

