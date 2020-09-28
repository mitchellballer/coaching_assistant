import pytest
from flask import g, session
from flaskr.db import get_db

def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a','coach_or_athlete': 'athlete'}
    )
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        assert get_db().execute(
            "select * from athlete where username = 'a'",
        ).fetchone() is not None

@pytest.mark.parametrize(('username', 'password', 'coach_or_athlete','message'), (
    ('', '', 'athlete', b'Username is required.'),
    ('a', '', 'athlete', b'Password is required.'),
    ('test', 'test', 'athlete', b'already registered'),
))
def test_register_validate_input(client, username, password, coach_or_athlete, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password, 'coach_or_athlete': coach_or_athlete}
    )
    assert message in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.athlete['username'] == 'test'

@pytest.mark.parametrize(('username', 'password', 'coach_or_athlete', 'message'), (
    ('a', 'test','athlete', b'Incorrect username.'),
    ('test', 'a','athlete', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, coach_or_athlete, message):
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
