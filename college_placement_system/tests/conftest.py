import os
import sys
import pytest

# Ensure app is discoverable from tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db as _db
from app.models import Department, Company, Student, Placement, Prediction, Eligibility, AdminUser


@pytest.fixture(scope='session')
def app():
    """Create and configure a Flask application for automated testing."""
    test_app = create_app('testing')
    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Provide a clean database session per test function."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        # Clean tables
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture(scope='function')
def client(app, db):
    """Provide a Flask test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def seed_basic_data(db):
    """Seed basic department, company and student data for route tests."""
    dept1 = Department(department_name='Computer Science and Engineering', department_code='CSE')
    dept2 = Department(department_name='Mechanical Engineering', department_code='MECH')
    db.session.add_all([dept1, dept2])
    db.session.flush()

    comp1 = Company(
        company_name='Google',
        job_role='Software Engineer',
        minimum_cgpa=8.0,
        maximum_arrears=0,
        package=20.0,
        graduation_year=2025
    )
    comp1.eligible_departments.append(dept1)

    comp2 = Company(
        company_name='TCS',
        job_role='Systems Engineer',
        minimum_cgpa=6.0,
        maximum_arrears=1,
        package=3.8,
        graduation_year=2025
    )
    comp2.eligible_departments.extend([dept1, dept2])

    db.session.add_all([comp1, comp2])
    db.session.flush()

    student1 = Student(
        register_number='REG2025CSE001',
        name='Alice Smith',
        email='alice@example.com',
        phone='9876543210',
        department_id=dept1.id,
        cgpa=8.5,
        arrears=0,
        graduation_year=2025,
        aptitude_score=85,
        technical_score=90,
        communication_score=88,
        internship_experience=1,
        skills='Python, SQL'
    )

    student2 = Student(
        register_number='REG2025MECH002',
        name='Bob Jones',
        email='bob@example.com',
        phone='9876543211',
        department_id=dept2.id,
        cgpa=6.5,
        arrears=1,
        graduation_year=2025,
        aptitude_score=60,
        technical_score=55,
        communication_score=65,
        internship_experience=0,
        skills='AutoCAD'
    )

    db.session.add_all([student1, student2])
    db.session.flush()

    admin = AdminUser(username='admin')
    admin.set_password('admin123')
    db.session.add(admin)

    db.session.commit()

    return {
        'dept_cse': dept1,
        'dept_mech': dept2,
        'comp_google': comp1,
        'comp_tcs': comp2,
        'student_alice': student1,
        'student_bob': student2,
        'admin': admin
    }

