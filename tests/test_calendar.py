import pytest
from flaskr.db import get_db
import datetime

def test_list(client, auth):
    response = client.get('/')
    assert b"Redirecting" in response.data

    auth.login()
    response = client.get('/list')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test' in response.data

@pytest.mark.parametrize('path', (
    '/create',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'

def test_create(client, auth, app):
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'
    assert client.get('/create').status_code == 200
    response = client.post('/create', data={'title': 'created', 'description': '', 'start_date_year': 2020, 'start_date_month': 1, 'start_date_day': 10, 'distance': 5, 'duration': "50:00"})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM activity').fetchone()[0]
        assert count == 2

def test_create_validate(client, auth):
    auth.login()
    response = client.post('/create', data={'title': '', 'description': '', 'start_date_year': 2020, 'start_date_month': 1, 'start_date_day': 10, 'distance': 5, 'duration': "50:00"})
    assert b'Title is required' in response.data



@pytest.mark.parametrize(('duration', 'title', 'success'), (
    ('01:10', 'Hello World', True),
    ('99:99', 'Hello World', False),
    ('1:10:10', 'Second', True),
    ('01:00:00', '6 digits', True),
    ('23:59:59.99', 'max', True),
    ('59:59.99', '4 digit max', True),
    ('59.99', '2 digit max', True),
    ('00:00:00.00', 'min', True),
    ('00:00.00', '4 digit min', True),
    ('00.00', '2 digit min', True),
    ('0.1', 'decimal', True),
    ('25:00:00', 'too many hours', False),
    ('00:61:00', 'too many minutes', False),
    ('00:00:61', 'too many seconds', False),
    ('1010', 'missing colon', False),
    ('asdf', 'wont work', False),
))
def test_create_duration(client, auth, app, duration, title, success):
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'
    assert client.get('/create').status_code == 200
    response = client.post('/create', data={'title': title, 'description': '', 'start_date_year': 2020, 'start_date_month': 1, 'start_date_day': 10, 'distance': 5, 'duration': duration})

    with app.app_context():
        db = get_db()
        count = db.execute(
            'SELECT COUNT(id) FROM activity WHERE title = ?',
            (title,)).fetchone()[0]
        if success:
            assert count == 1
        else:
            assert b'Invalid duration format' in response.data
