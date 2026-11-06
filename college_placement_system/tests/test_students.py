import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Student, Department


def test_student_insertion(db, seed_basic_data):
    """Test inserting a new student and verifying its properties."""
    cse_dept = seed_basic_data['dept_cse']
    student = Student(
        register_number='REG2025CSE099',
        name='Charlie Brown',
        email='charlie@example.com',
        phone='9123456789',
        department_id=cse_dept.id,
        cgpa=9.1,
        arrears=0,
        graduation_year=2025,
        aptitude_score=92,
        technical_score=95,
        communication_score=90,
        internship_experience=2,
        skills='Python, Machine Learning'
    )
    db.session.add(student)
    db.session.commit()

    saved = Student.query.filter_by(register_number='REG2025CSE099').first()
    assert saved is not None
    assert saved.name == 'Charlie Brown'
    assert saved.cgpa == 9.1
    assert saved.department.department_code == 'CSE'


def test_student_update(db, seed_basic_data):
    """Test updating existing student details."""
    student = seed_basic_data['student_alice']
    student.cgpa = 8.9
    student.skills = 'Python, Flask, PySpark'
    db.session.commit()

    updated = db.session.get(Student, student.id)
    assert updated.cgpa == 8.9
    assert 'PySpark' in updated.skills


def test_student_deletion(db, seed_basic_data):
    """Test deleting a student."""
    student = seed_basic_data['student_bob']
    student_id = student.id
    db.session.delete(student)
    db.session.commit()

    assert db.session.get(Student, student_id) is None


def test_duplicate_email_validation(db, seed_basic_data):
    """Test that duplicate email throws IntegrityError."""
    cse_dept = seed_basic_data['dept_cse']
    duplicate_student = Student(
        register_number='REG2025CSE999',
        name='Duplicate Email',
        email='alice@example.com',  # Already exists for alice
        department_id=cse_dept.id,
        cgpa=7.5,
        graduation_year=2025
    )
    db.session.add(duplicate_student)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_duplicate_reg_no_validation(db, seed_basic_data):
    """Test that duplicate register number throws IntegrityError."""
    cse_dept = seed_basic_data['dept_cse']
    duplicate_student = Student(
        register_number='REG2025CSE001',  # Already exists for alice
        name='Duplicate Reg',
        email='newunique@example.com',
        department_id=cse_dept.id,
        cgpa=7.5,
        graduation_year=2025
    )
    db.session.add(duplicate_student)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_foreign_key_relationship(db, seed_basic_data):
    """Test student-department relationship navigation."""
    student = seed_basic_data['student_alice']
    assert student.department is not None
    assert student.department.department_code == 'CSE'
    assert student in student.department.students.all()
