from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Student, Company, Placement, Department, Eligibility
from app.services.analytics_service import AnalyticsService
from app.services.eligibility_service import EligibilityService
from app.services.prediction_service import PredictionService

api_bp = Blueprint('api', __name__)


# ---------------- STUDENT APIS ----------------

@api_bp.route('/students', methods=['GET'])
def get_students():
    """Retrieve list of students with optional filtering and pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search_q = request.args.get('q', '').strip()
    dept_id = request.args.get('department_id', type=int)

    query = Student.query

    if search_q:
        query = query.filter(
            (Student.name.ilike(f'%{search_q}%')) |
            (Student.register_number.ilike(f'%{search_q}%')) |
            (Student.email.ilike(f'%{search_q}%'))
        )

    if dept_id:
        query = query.filter_by(department_id=dept_id)

    pagination = query.order_by(Student.register_number.asc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'per_page': pagination.per_page,
        'students': [s.to_dict() for s in pagination.items]
    }), 200


@api_bp.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Retrieve a single student by ID."""
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'error': 'Student not found', 'student_id': student_id}), 404
    return jsonify(student.to_dict()), 200


@api_bp.route('/students', methods=['POST'])
def create_student():
    """Register a new student via REST API."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON body'}), 400

    reg_no = data.get('register_number')
    name = data.get('name')
    email = data.get('email')
    dept_id = data.get('department_id')
    cgpa = data.get('cgpa')

    errors = []
    if not reg_no:
        errors.append("register_number is required")
    elif Student.query.filter_by(register_number=reg_no).first():
        errors.append(f"Student with register_number '{reg_no}' already exists")

    if not name:
        errors.append("name is required")

    if not email:
        errors.append("email is required")
    elif Student.query.filter_by(email=email).first():
        errors.append(f"Student with email '{email}' already exists")

    if not dept_id or not db.session.get(Department, dept_id):
        errors.append("Valid department_id is required")

    if cgpa is None or not (0.0 <= float(cgpa) <= 10.0):
        errors.append("cgpa must be between 0.0 and 10.0")

    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    try:
        student = Student(
            register_number=reg_no,
            name=name,
            email=email,
            phone=data.get('phone'),
            department_id=dept_id,
            cgpa=float(cgpa),
            arrears=int(data.get('arrears', 0)),
            graduation_year=int(data.get('graduation_year', 2025)),
            aptitude_score=int(data.get('aptitude_score', 0)),
            technical_score=int(data.get('technical_score', 0)),
            communication_score=int(data.get('communication_score', 0)),
            internship_experience=int(data.get('internship_experience', 0)),
            skills=data.get('skills', '')
        )
        db.session.add(student)
        db.session.commit()
        return jsonify(student.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database transaction error', 'message': str(e)}), 500


@api_bp.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    """Update existing student details."""
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON body'}), 400

    if 'name' in data:
        student.name = data['name']
    if 'phone' in data:
        student.phone = data['phone']
    if 'cgpa' in data:
        cgpa_val = float(data['cgpa'])
        if not (0.0 <= cgpa_val <= 10.0):
            return jsonify({'error': 'cgpa must be between 0.0 and 10.0'}), 400
        student.cgpa = cgpa_val
    if 'arrears' in data:
        student.arrears = int(data['arrears'])
    if 'skills' in data:
        student.skills = data['skills']
    if 'aptitude_score' in data:
        student.aptitude_score = int(data['aptitude_score'])
    if 'technical_score' in data:
        student.technical_score = int(data['technical_score'])
    if 'communication_score' in data:
        student.communication_score = int(data['communication_score'])
    if 'internship_experience' in data:
        student.internship_experience = int(data['internship_experience'])

    db.session.commit()
    return jsonify(student.to_dict()), 200


@api_bp.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete student record."""
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': f'Student {student_id} deleted successfully'}), 200


# ---------------- COMPANY APIS ----------------

@api_bp.route('/companies', methods=['GET'])
def get_companies():
    """Retrieve all recruiting companies."""
    companies = Company.query.order_by(Company.company_name.asc()).all()
    return jsonify([c.to_dict() for c in companies]), 200


@api_bp.route('/companies', methods=['POST'])
def create_company():
    """Add a new company via REST API."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON body'}), 400

    name = data.get('company_name')
    role = data.get('job_role')
    min_cgpa = data.get('minimum_cgpa')
    package = data.get('package')
    grad_year = data.get('graduation_year')
    dept_ids = data.get('eligible_departments', [])

    if not name or not role or min_cgpa is None or package is None or not grad_year:
        return jsonify({'error': 'Missing required fields (company_name, job_role, minimum_cgpa, package, graduation_year)'}), 400

    try:
        company = Company(
            company_name=name,
            job_role=role,
            minimum_cgpa=float(min_cgpa),
            maximum_arrears=int(data.get('maximum_arrears', 0)),
            package=float(package),
            graduation_year=int(grad_year)
        )
        for d_id in dept_ids:
            dept = db.session.get(Department, d_id)
            if dept:
                company.eligible_departments.append(dept)

        db.session.add(company)
        db.session.commit()
        return jsonify(company.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database transaction error', 'message': str(e)}), 500


# ---------------- PLACEMENT APIS ----------------

@api_bp.route('/placements', methods=['GET'])
def get_placements():
    """Retrieve placements with optional status filtering."""
    status = request.args.get('status')
    query = Placement.query
    if status:
        query = query.filter_by(status=status)
    placements = query.order_by(Placement.id.desc()).all()
    return jsonify([p.to_dict() for p in placements]), 200


# ---------------- ANALYTICS APIS ----------------

@api_bp.route('/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Retrieve high-level placement KPIs computed with NumPy and Pandas."""
    summary = AnalyticsService.generate_summary_metrics()
    return jsonify(summary), 200


@api_bp.route('/analytics/departments', methods=['GET'])
def get_department_analytics():
    """Retrieve department-wise placement statistics."""
    dept_stats = AnalyticsService.department_wise_analytics()
    return jsonify(dept_stats), 200


# ---------------- ELIGIBILITY APIS ----------------

@api_bp.route('/eligibility/check', methods=['POST'])
def check_eligibility():
    """Check student eligibility for a specific company."""
    data = request.get_json()
    if not data or 'student_id' not in data or 'company_id' not in data:
        return jsonify({'error': 'student_id and company_id are required'}), 400

    result = EligibilityService.check_and_record(data['student_id'], data['company_id'])
    if 'error' in result:
        return jsonify(result), 404
    return jsonify(result), 200


# ---------------- PREDICTION APIS ----------------

@api_bp.route('/predictions/<int:student_id>', methods=['POST'])
def predict_student_placement(student_id):
    """Run Random Forest prediction for a specific student and persist outcome."""
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    try:
        result = PredictionService.predict_for_student(student, save_to_db=True)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': 'Inference error', 'message': str(e)}), 500

