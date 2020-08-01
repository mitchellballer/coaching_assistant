from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
import datetime

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('calendar', __name__)

#get the activities to display on the calendar. Return them with the render template
@bp.route('/')
def index():
    db = get_db()
    activities = db.execute(
        'SELECT p.id, title, description, start_date, athlete_id, username, distance, duration'
        ' FROM activity p JOIN athlete u ON p.athlete_id = u.id'
        ' ORDER BY start_date DESC'
    ).fetchall()
    return render_template('calendar/index.html', activities=activities)

#create view. Must be logged in to view
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
        print('hello world')

        if not title:
            error = 'Title is required'
        #if they don't provide a date, use the current datetime
        if not start_date:
            start_date = datetime.datetime.now()
        if not distance:
            print('no distance')
        else:
            print(f'distance: {distance}')
        if not duration:
            print('no duration')
        else:
            print(f'duration: {duration}')

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
            hello = db.execute(
                'SELECT * from activity;')
            #we can see the distance and duration are loaded into the database.... so why are they still not appearing in the calendar?
            print(tuple(hello.fetchone()))
            return redirect(url_for('calendar.index'))
    return render_template('activity/create.html')