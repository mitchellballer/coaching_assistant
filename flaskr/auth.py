import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)
        
        #add them to the database
        if error is None:
            db.execute(
                'INSERT INTO athlete (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        athlete = db.execute(
            'SELECT * FROM athlete WHERE username = ?', (username,)
        ).fetchone()

        if athlete is None:
            error = 'Incorrect Username.'
        elif not check_password_hash(athlete['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = athlete['id']
            return redirect(url_for('index'))
        
        flash(error)
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_athlete():
    athlete_id = session.get('athlete_id')

    if athlete_id is None:
        g.athlete = None
    else:
        g.athlete = get_db().execute(
            'SELECT * FROM athlete WHERE athlete_id = ?', (athlete_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#decorator to return a wrapped view that requires login
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.athlete is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)

    return wrapped_view