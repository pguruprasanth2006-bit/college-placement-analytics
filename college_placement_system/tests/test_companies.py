import pytest
from app.models import Company, Department


def test_company_creation_and_depts(db, seed_basic_data):
    """Test company creation and association with multiple departments."""
    cse = seed_basic_data['dept_cse']
    mech = seed_basic_data['dept_mech']

    company = Company(
        company_name='Infosys',
        job_role='Systems Engineer',
        minimum_cgpa=6.5,
        maximum_arrears=1,
        package=4.5,
        graduation_year=2025
    )
    company.eligible_departments.extend([cse, mech])
    db.session.add(company)
    db.session.commit()

    saved = Company.query.filter_by(company_name='Infosys').first()
    assert saved is not None
    assert len(saved.eligible_departments) == 2
    dept_codes = [d.department_code for d in saved.eligible_departments]
    assert 'CSE' in dept_codes
    assert 'MECH' in dept_codes


def test_company_update(db, seed_basic_data):
    """Test updating company requirements."""
    company = seed_basic_data['comp_google']
    company.package = 24.5
    company.minimum_cgpa = 8.8
    db.session.commit()

    updated = db.session.get(Company, company.id)
    assert updated.package == 24.5
    assert updated.minimum_cgpa == 8.8


def test_company_deletion(db, seed_basic_data):
    """Test deleting a company."""
    company = seed_basic_data['comp_tcs']
    company_id = company.id
    db.session.delete(company)
    db.session.commit()

    assert db.session.get(Company, company_id) is None
