from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('calendar', __name__)

#get the activities to display on the calendar. Return them with the render template
@bp.route('/')
def index():
    db = get_db()
    activities = db.execute(
        'SELECT p.id, title, description, start_date, athlete_id, username'
        ' FROM activity p JOIN athlete u ON p.athlete_id = u.athlete_id'
        ' ORDER BY start_date DESC'
    ).fetchall()
    return render_template('calendar/index.html', activities=activities)