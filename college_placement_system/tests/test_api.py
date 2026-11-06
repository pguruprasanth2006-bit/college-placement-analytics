import pytest
import json


def test_api_get_students(client, seed_basic_data):
    """Test GET /api/students returns list and pagination metadata."""
    response = client.get('/api/students')
    assert response.status_code == 200
    data = response.get_json()
    assert 'students' in data
    assert len(data['students']) == 2
    assert data['total'] == 2


def test_api_get_single_student(client, seed_basic_data):
    """Test GET /api/students/<id>."""
    alice = seed_basic_data['student_alice']
    response = client.get(f'/api/students/{alice.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Alice Smith'
    assert data['register_number'] == 'REG2025CSE001'

    # Non-existent
    resp_404 = client.get('/api/students/99999')
    assert resp_404.status_code == 404


def test_api_create_student_success(client, seed_basic_data):
    """Test POST /api/students with valid data."""
    dept = seed_basic_data['dept_cse']
    payload = {
        'register_number': 'REG2025CSE777',
        'name': 'API Student',
        'email': 'api_student@example.com',
        'phone': '9876543219',
        'department_id': dept.id,
        'cgpa': 8.2,
        'arrears': 0,
        'graduation_year': 2025,
        'aptitude_score': 80,
        'technical_score': 85,
        'communication_score': 75,
        'internship_experience': 1,
        'skills': 'Python, API'
    }
    response = client.post('/api/students', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 201
    data = response.get_json()
    assert data['register_number'] == 'REG2025CSE777'


def test_api_create_student_validation_failure(client, seed_basic_data):
    """Test POST /api/students returns 400 when CGPA is invalid or required fields missing."""
    payload = {
        'register_number': '',
        'name': '',
        'email': 'invalid',
        'cgpa': 15.0  # Invalid CGPA > 10
    }
    response = client.post('/api/students', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'details' in data


def test_api_update_student(client, seed_basic_data):
    """Test PUT /api/students/<id>."""
    alice = seed_basic_data['student_alice']
    update_data = {'cgpa': 9.2, 'skills': 'Python, Docker, Kubernetes'}
    response = client.put(f'/api/students/{alice.id}', data=json.dumps(update_data), content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['cgpa'] == 9.2
    assert 'Docker' in data['skills']


def test_api_delete_student(client, seed_basic_data):
    """Test DELETE /api/students/<id>."""
    bob = seed_basic_data['student_bob']
    response = client.delete(f'/api/students/{bob.id}')
    assert response.status_code == 200

    # Ensure deleted
    get_resp = client.get(f'/api/students/{bob.id}')
    assert get_resp.status_code == 404


def test_api_companies(client, seed_basic_data):
    """Test GET and POST /api/companies."""
    # GET
    response = client.get('/api/companies')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 2

    # POST
    dept = seed_basic_data['dept_cse']
    new_company = {
        'company_name': 'Oracle',
        'job_role': 'Database Engineer',
        'minimum_cgpa': 7.5,
        'maximum_arrears': 0,
        'package': 14.0,
        'graduation_year': 2025,
        'eligible_departments': [dept.id]
    }
    post_resp = client.post('/api/companies', data=json.dumps(new_company), content_type='application/json')
    assert post_resp.status_code == 201


def test_api_analytics_endpoints(client, seed_basic_data):
    """Test GET /api/analytics/summary and GET /api/analytics/departments."""
    summary_resp = client.get('/api/analytics/summary')
    assert summary_resp.status_code == 200
    summary_data = summary_resp.get_json()
    assert 'total_students' in summary_data
    assert 'placement_percentage' in summary_data

    dept_resp = client.get('/api/analytics/departments')
    assert dept_resp.status_code == 200
    dept_data = dept_resp.get_json()
    assert isinstance(dept_data, list)


def test_api_eligibility_check(client, seed_basic_data):
    """Test POST /api/eligibility/check."""
    alice = seed_basic_data['student_alice']
    google = seed_basic_data['comp_google']

    payload = {'student_id': alice.id, 'company_id': google.id}
    response = client.post('/api/eligibility/check', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['is_eligible'] is True


def test_api_prediction(client, seed_basic_data):
    """Test POST /api/predictions/<student_id>."""
    alice = seed_basic_data['student_alice']
    response = client.post(f'/api/predictions/{alice.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert 'probability' in data
    assert 'predicted_status' in data

