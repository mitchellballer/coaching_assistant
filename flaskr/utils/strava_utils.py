import configparser
import requests
from flaskr.db import get_db
from flask import flash
from . import token_utils, db_utils


# function that just prints current info about our athlete, state of tokens
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


# save given activity to database for given athlete
# only save activity if it doesn't already exist in the database
# input is a single activity in json form provided by strava
# TODO: reevaluate how activity start time is stored. Epoch? String? datetime?
def save_activity(activity, athlete_id):
    title = activity['name']
    start = activity['start_date_local'].replace('T', ' ').replace('Z', '')
    description = 'sample description'  # activity['description']
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


# query strava for athlete's activities between start and end date then save to database
# Assumes athlete has a valid bearer token TODO: error check valid bearer token
# Assumes before/after are epoch timestamp TODO: error check before/after
def strava_activities(bearer_token, athlete_id, before, after, max_activities, refresh_token):
    if not token_utils.has_valid_token():
        client_id, secret = check_prerequisites()
        token_utils.refresh_existing_token(client_id, secret, refresh_token)
        bearer_token = token_utils.get_bearer_token(athlete_id)
    base = 'https://www.strava.com/api/v3/athlete/activities'
    parameters = {'before': before, 'after': after, 'per_page': max_activities}
    header = {'Authorization': 'Bearer ' + bearer_token}
    response = requests.get(base, headers=header, params=parameters)
    activities = response.json()
    if response.status_code == 200:
        for activity in activities:
            save_activity(activity, athlete_id)
        flash(f"{len(activities)} activities pulled.")

    else:
        flash("There was an error pulling activities from strava.")
        print(f"info on respone: {response.status_code}")
        print(response)


# Function to pull client_id and client_secret from config
def check_prerequisites():
    # load client properties from config.properties
    config = configparser.ConfigParser()
    config_file = 'config.properties'
    config.read(config_file)
    id = config['CLIENT']['client_id']
    secret = config['CLIENT']['client_secret']
    # make sure we found client properties
    error = None

    if not id:
        error = 'No client id. Please load client ID into config.properties on the server'
    if not secret:
        error = 'No client secret. Please load client ID into config.properties on the server'
    if error is not None:
        flash(error)

    return id, secret
