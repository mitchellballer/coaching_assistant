import datetime

from flask import flash, Flask
from flask_sqlalchemy import SQLAlchemy
from flaskr.db import get_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class Activity(db.Model):
    def __init__(self, activity_id, title, description, start_date, athlete_id, distance, duration):
        self.activity_id = activity_id
        self.title = title
        self.description = description
        self.start_date = start_date
        self.athlete_id = athlete_id
        self.distance = distance
        self.duration = duration

    def save(self):
        error = None

        if not self.title:
            error = 'title not given'
        elif not self.athlete_id:
            error = 'athlete id not given'

        if not self.start_date:
            self.start_date == datetime.datetime.now()
        if not self.distance:
            self.distance = 0
        if not self.duration:
            self.duration = 0

        if error is not None:
            flash(error)
        #no activity id given so this activity didn't come from strava. Just don't pass to db
        elif not self.activity_id:
            db = get_db()
            db.execute(
                'INSERT INTO activity (title, description, start_date, athlete_id, distance, duration)'
                'VALUES (?, ?, ?, ?, ?, ?)',
                (self.title, )
            )
