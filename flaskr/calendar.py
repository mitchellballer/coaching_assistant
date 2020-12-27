from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import datetime
import time

from flaskr.auth import login_required
from flaskr.db import get_db
from .utils import strava_utils
from .utils.my_calendar import Month, Week

bp = Blueprint('calendar', __name__)


# get the activities to display on the calendar. Return them with the render template
@bp.route('/list')
def list():
    db = get_db()
    activities = db.execute(
        'SELECT p.id, title, description, start_date, athlete_id, username, distance, duration'
        ' FROM activity p JOIN athlete u ON p.athlete_id = u.id'
        ' ORDER BY start_date DESC'
    ).fetchall()

    return render_template('calendar/list.html', activities=activities)


@bp.route('/')
@login_required
def index():
    return redirect(url_for('calendar.month', year=datetime.datetime.now().year, month=datetime.datetime.now().month))


@bp.route('/month/<int:year>/<int:month>')
@login_required
def month(year, month):
    new_month = Month(year, month)
    new_month.add_activities(g.athlete['id'])
    return render_template('calendar/month.html', month=new_month)

@bp.route('/week/<int:year>/<int:month>/<int:week>')
@login_required
def week(year, month, week):
    month = Month(datetime.datetime.now().year, datetime.datetime.now().month)
    week = month.get_week_from_day(datetime.datetime.now().day)
    week.add_activities(g.athlete['id'])
    return render_template('calendar/week.html', week=week, month=month)

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
            return redirect(url_for('calendar.list'))
    return render_template('activity/create.html')


@bp.route('/pull', methods=('GET', 'POST'))
@login_required
def pull():
    if request.method == 'POST':
        bearer_token = g.athlete['strava_bearer_token']
        athlete_id = g.athlete['id']
        refresh_token = g.athlete['strava_refresh_token']
        pull_range = request.form['range']
        before = int(time.time())
        after = int(time.time())
        max_activities = 30
        flash(f"Range: {pull_range}")

        if pull_range == "most_recent":
            after = 0
            max_activities = 1
            #strava_utils.strava_activities(bearer_token, athlete_id, time.time(), 0, 1)
        elif pull_range == "today":
            after = int(time.time() - (60 * 60 * 24))
            # no one has more than 30 activities in a day.. right?
        elif pull_range == "week":
            after = int(time.time() - (60 * 60 * 24 * 7))
            max_activities = 100
        elif pull_range == "month":
            #TODO need a more elegant way of saying the past month/day/week.
            after = int(time.time() - (60 * 60 * 24 * 7 * 30))
        strava_utils.strava_activities(bearer_token, athlete_id, before, after, max_activities, refresh_token)

        return redirect(url_for('calendar.list'))

    return render_template('activity/pull.html')