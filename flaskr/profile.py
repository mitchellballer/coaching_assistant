from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('profile', __name__)

@bp.route('/profile')
@login_required
def index():
    return render_template('profile/index.html')

@bp.route('/connect')
@login_required
def connect():
    #put code to connect to garmin here
    print('connecting to strava')
    print('redirecting to profile page')
    return redirect(url_for('profile.index'))