from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import datetime

from flaskr.auth import login_required
from flaskr.db import get_db
from .utils import strava_utils

bp = Blueprint('calendar', __name__)


# get the activities to display on the calendar. Return them with the render template
@bp.route('/')
def index():
    db = get_db()
    activities = db.execute(
        'SELECT p.id, title, description, start_date, athlete_id, username, distance, duration'
        ' FROM activity p JOIN athlete u ON p.athlete_id = u.id'
        ' ORDER BY start_date DESC'
    ).fetchall()
    strava_utils.hello_world()

    return render_template('calendar/index.html', activities=activities)


# create view. Must be logged in to view
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        start_date = request.form['start_date']
        distance = request.form['distance']
        duration = request.form['duration']
        error = None

        if not title:
            error = 'Title is required'
        # if they don't provide a date, use the current datetime
        if not start_date:
            start_date = datetime.datetime.now()
        # if they don't provide distance, mark as zero
        if not distance:
            distance = 0
        # if they don't provide a duration, mark as zero?
        if not duration:
            duration = 0

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO activity (title, description, start_date, athlete_id, distance, duration)'
                ' VALUES (?, ?, ?, ?, ?, ?)',
                (title, description, start_date, g.athlete['id'], distance, duration)
            )
            db.commit()
            return redirect(url_for('calendar.index'))
    return render_template('activity/create.html')