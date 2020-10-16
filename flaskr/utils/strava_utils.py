from flaskr.db import get_db
from flask import flash

class print_stuff:

    #function that just prints current info about our athlete, state of tokens etc.
    def print_current_state(athlete_id, bearer_token, bearer_token_expiration, refresh_token, strava_id):
        print("Printing current state")
        print(f"Athlete id: {athlete_id}")
        print(f"strava bearer token: {bearer_token}")
        print(f"strava bearer token expiration: {bearer_token_expiration}")
        print(f"strava refresh token: {refresh_token}")
        print(f"strava athlete id: {strava_id}")

    def hello_world():
        print("Hello world")
        flash("hello world!")

class db_utils:

#save given activity to database for given athlete
#only save activity if it doesn't already exist in the database
#input is a single activity in json form provided by strava
    def save_activity(activity, athlete_id):
        title = activity['name']
        start = activity['start_date'].replace('T', ' ').replace('Z','')
        description = activity['description']
        distance = activity['distance']
        duration = activity['elapsed_time']
        strava_id = activity['id']
        db = get_db()
        error = None

        if not activity:
            error = 'no activity given'
        elif not strava_id:
            error = 'no strava activity id given'
        elif db.execute('SELECT id FROM activity WHERE id = ?', (strava_id,)).fetchone() is not None:
            error = 'activity ID: {} already exists in the database'.format(strava_id)

        if error is None:
            db.execute(
                'INSERT INTO activity (id, start_date, title, description, distance, duration, athlete_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                (strava_id, start, title, description, distance, duration, athlete_id)
            )
            db.commit()
            return True
        else:
            flash(error)
            return False