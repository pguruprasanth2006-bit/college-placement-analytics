from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.auth import login_required
from app.models import Company, Department

company_bp = Blueprint('companies', __name__)


@company_bp.route('/')
@login_required
def index():
    """List all recruiting companies with requirements, package and eligible departments."""
    companies = Company.query.order_by(Company.package.desc()).all()
    return render_template('companies.html', companies=companies)


@company_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new company recruitment drive with criteria."""
    departments = Department.query.order_by(Department.department_name.asc()).all()

    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        job_role = request.form.get('job_role', '').strip()
        min_cgpa = request.form.get('minimum_cgpa', type=float)
        max_arrears = request.form.get('maximum_arrears', 0, type=int)
        package = request.form.get('package', type=float)
        grad_year = request.form.get('graduation_year', type=int)
        dept_ids = request.form.getlist('department_ids', type=int)

        errors = []
        if not company_name:
            errors.append("Company name is required.")
        if not job_role:
            errors.append("Job role is required.")
        if min_cgpa is None or min_cgpa < 0.0 or min_cgpa > 10.0:
            errors.append("Minimum CGPA must be between 0.0 and 10.0.")
        if max_arrears is None or max_arrears < 0:
            errors.append("Maximum allowed arrears cannot be negative.")
        if package is None or package < 0:
            errors.append("Package (LPA) cannot be negative.")
        if not grad_year:
            errors.append("Graduation year is required.")
        if not dept_ids:
            errors.append("Please select at least one eligible department.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('company_form.html', company=None, departments=departments, form_data=request.form)

        try:
            company = Company(
                company_name=company_name,
                job_role=job_role,
                minimum_cgpa=min_cgpa,
                maximum_arrears=max_arrears,
                package=package,
                graduation_year=grad_year
            )
            for d_id in dept_ids:
                d = db.session.get(Department, d_id)
                if d:
                    company.eligible_departments.append(d)

            db.session.add(company)
            db.session.commit()
            flash(f"Company '{company_name}' ({job_role}) added successfully!", 'success')
            return redirect(url_for('companies.index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding company: {str(e)}", 'danger')

    return render_template('company_form.html', company=None, departments=departments, form_data={})


@company_bp.route('/edit/<int:company_id>', methods=['GET', 'POST'])
@login_required
def edit(company_id):
    """Edit company recruitment details."""
    company = db.session.get(Company, company_id)
    if not company:
        flash('Company not found.', 'danger')
        return redirect(url_for('companies.index'))

    departments = Department.query.order_by(Department.department_name.asc()).all()

    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        job_role = request.form.get('job_role', '').strip()
        min_cgpa = request.form.get('minimum_cgpa', type=float)
        max_arrears = request.form.get('maximum_arrears', 0, type=int)
        package = request.form.get('package', type=float)
        grad_year = request.form.get('graduation_year', type=int)
        dept_ids = request.form.getlist('department_ids', type=int)

        errors = []
        if not company_name:
            errors.append("Company name is required.")
        if not job_role:
            errors.append("Job role is required.")
        if min_cgpa is None or min_cgpa < 0.0 or min_cgpa > 10.0:
            errors.append("Minimum CGPA must be between 0.0 and 10.0.")
        if max_arrears is None or max_arrears < 0:
            errors.append("Maximum allowed arrears cannot be negative.")
        if package is None or package < 0:
            errors.append("Package (LPA) cannot be negative.")
        if not grad_year:
            errors.append("Graduation year is required.")
        if not dept_ids:
            errors.append("Please select at least one eligible department.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('company_form.html', company=company, departments=departments, form_data=request.form)

        try:
            company.company_name = company_name
            company.job_role = job_role
            company.minimum_cgpa = min_cgpa
            company.maximum_arrears = max_arrears
            company.package = package
            company.graduation_year = grad_year

            # Update association table
            company.eligible_departments.clear()
            for d_id in dept_ids:
                d = db.session.get(Department, d_id)
                if d:
                    company.eligible_departments.append(d)

            db.session.commit()
            flash(f"Company '{company_name}' updated successfully!", 'success')
            return redirect(url_for('companies.index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating company: {str(e)}", 'danger')

    return render_template('company_form.html', company=company, departments=departments, form_data={})


@company_bp.route('/delete/<int:company_id>', methods=['POST'])
@login_required
def delete(company_id):
    """Delete a company."""
    company = db.session.get(Company, company_id)
    if not company:
        flash('Company not found.', 'danger')
        return redirect(url_for('companies.index'))

    try:
        name = company.company_name
        db.session.delete(company)
        db.session.commit()
        flash(f"Company '{name}' was deleted successfully.", 'info')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting company: {str(e)}", 'danger')

    return redirect(url_for('companies.index'))

