import pytest
from app.models import Student, Company, Department
from app.services.eligibility_service import EligibilityService


def test_eligible_student(db, seed_basic_data):
    """Test student who satisfies all company criteria."""
    student = seed_basic_data['student_alice']  # CGPA 8.5, 0 arrears, 2025, CSE
    company = seed_basic_data['comp_google']   # Min CGPA 8.0, 0 arrears, 2025, CSE eligible

    is_eligible, reasons = EligibilityService.evaluate_student(student, company)
    assert is_eligible is True
    assert len(reasons) == 0


def test_cgpa_failure(db, seed_basic_data):
    """Test student failing minimum CGPA requirement."""
    student = seed_basic_data['student_bob']   # CGPA 6.5
    company = seed_basic_data['comp_google']   # Min CGPA 8.0

    is_eligible, reasons = EligibilityService.evaluate_student(student, company)
    assert is_eligible is False
    assert any("CGPA" in r for r in reasons)


def test_arrears_failure(db, seed_basic_data):
    """Test student failing maximum allowed arrears requirement."""
    cse = seed_basic_data['dept_cse']
    student_with_arrears = Student(
        register_number='REG2025CSE050',
        name='David Arrears',
        email='david@example.com',
        department_id=cse.id,
        cgpa=8.8,
        arrears=2,  # 2 arrears
        graduation_year=2025
    )
    db.session.add(student_with_arrears)
    db.session.commit()

    company = seed_basic_data['comp_google']  # Max arrears 0
    is_eligible, reasons = EligibilityService.evaluate_student(student_with_arrears, company)
    assert is_eligible is False
    assert any("arrears" in r.lower() for r in reasons)


def test_department_failure(db, seed_basic_data):
    """Test student belonging to an ineligible department."""
    student_mech = seed_basic_data['student_bob']  # MECH department
    company = seed_basic_data['comp_google']      # Only CSE eligible

    is_eligible, reasons = EligibilityService.evaluate_student(student_mech, company)
    assert is_eligible is False
    assert any("Department" in r for r in reasons)


def test_graduation_year_failure(db, seed_basic_data):
    """Test student graduating in a different year than drive requirement."""
    cse = seed_basic_data['dept_cse']
    student_2024 = Student(
        register_number='REG2024CSE010',
        name='Past Student',
        email='past@example.com',
        department_id=cse.id,
        cgpa=8.5,
        arrears=0,
        graduation_year=2024  # 2024 instead of 2025
    )
    db.session.add(student_2024)
    db.session.commit()

    company = seed_basic_data['comp_google']  # 2025
    is_eligible, reasons = EligibilityService.evaluate_student(student_2024, company)
    assert is_eligible is False
    assert any("Graduation year" in r for r in reasons)

