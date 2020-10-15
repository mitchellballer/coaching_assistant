import pytest
from flaskr.db import get_db
import datetime

def test_index(client, auth):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data


    auth.login()
    response = client.get('/')
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
    response = client.post('/create', data={'title': 'created', 'description': '', 'start_date': datetime.datetime.now(), 'distance': 5, 'duration': 5000})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM activity').fetchone()[0]
        assert count == 2

def test_create_validate(client, auth):
    auth.login()
    response = client.post('/create', data={'title': '', 'description': '', 'start_date': datetime.datetime.now(), 'distance': 5, 'duration': 5000})
    assert b'Title is required' in response.data
    