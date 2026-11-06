import pytest


def test_auth_protection_redirects(client):
    """Test that protected pages redirect unauthenticated visitors to login."""
    protected_urls = [
        '/',
        '/students/',
        '/students/add',
        '/companies/',
        '/companies/add',
        '/placements/',
        '/placements/add',
        '/eligibility/',
        '/analytics/',
        '/prediction/'
    ]
    for url in protected_urls:
        response = client.get(url, follow_redirects=False)
        assert response.status_code in (302, 308)
        assert '/login' in response.headers.get('Location', '')


def test_admin_login_success(client, seed_basic_data):
    """Test successful login with admin credentials."""
    response = client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Placement Overview Dashboard' in response.data or b'Dashboard' in response.data


def test_admin_login_failure(client, seed_basic_data):
    """Test login failure with wrong password."""
    response = client.post('/login', data={'username': 'admin', 'password': 'wrongpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data


def test_authenticated_access(client, seed_basic_data):
    """Test accessing protected dashboard and pages after logging in."""
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})

    resp_dashboard = client.get('/')
    assert resp_dashboard.status_code == 200
    assert b'Total Students' in resp_dashboard.data

    resp_students = client.get('/students/')
    assert resp_students.status_code == 200
    assert b'Alice Smith' in resp_students.data

    resp_companies = client.get('/companies/')
    assert resp_companies.status_code == 200
    assert b'Google' in resp_companies.data

