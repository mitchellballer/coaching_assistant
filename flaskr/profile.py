from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flaskr.auth import login_required
from flaskr.db import get_db
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from .utils.strava_utils import print_stuff, db_utils
from requests_oauthlib import OAuth2Session

import requests
import time

bp = Blueprint('profile', __name__)


@bp.route('/profile')
@login_required
def index():
    print_stuff.hello_world()

    return render_template('profile/index.html')


@bp.route('/authorized/')
def authorized():
    # did we get any useful information from this url?
    print("hello world")
    return redirect(url_for('profile.index'))


@bp.route('/connect', methods=('GET', 'POST'))
@login_required
def connect():
    print('gathering prerequisites')

    client_id, secret, athlete_id, bearer_token, token_exp, refresh_token, strava_id = db_utils.check_prerequisites()
    # put code to connect to strava here
    print('connecting to strava')

    # TODO get this redirecting to a page where we can use without the command line
    redirect_uri = 'http://localhost:5000/exchange_token'
    auth_url = 'https://www.strava.com/oauth/authorize'
    scope = 'activity:read'

    # if we don't have a bearer token or refresh token, get them.
    if bearer_token is None or refresh_token is None:
        oauth = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, scope=[scope])
        authorization_url, state = oauth.authorization_url(auth_url)
        authorization_url = authorization_url + '&approval_prompt=force'
        return redirect(authorization_url)

    # if we already have a short term token but it's expired, we should refresh
    elif token_exp < time.time():
        refresh_existing_token(client_id, secret, refresh_token)

    print('redirecting to profile page')
    return redirect(url_for('profile.index'))


@bp.route('/exchange_token', methods=('GET', 'POST'))
def exchange_token():
    print("starting exchange token function")
    token_url = 'https://www.strava.com/oauth/token'
    # TODO: a lot of this should be outsourced to it's own class. Call it authorization or token functions or something
    # All of this needs to be cleaned up
    client_id, secret, athlete_id, bearer_token, token_exp, refresh_token, strava_id = db_utils.check_prerequisites()
    if request.method == 'GET':
        authorization_response = request.url
        o = urlparse(authorization_response)
        query = parse_qs(o.query)
        if 'code' in query:
            authorization_code = query['code']
        else:
            print("No authorization code")

        # perform token exchange
        payload = {'client_id': client_id, 'secret': secret, 'code': authorization_code, 'grant_type': 'authorization_code'}
        r = requests.post(token_url, data=payload)

        if r.status_code == 200:
            bearer_token = r.json()['access_token']
            token_exp = r.json()['expires_at']
            refresh_token = r.json()['refresh_token']
            update_athlete_tokens(bearer_token, token_exp, refresh_token, True, g.athlete['id'])
            flash("connected to strava!")
        else:
            flash("there was an issue connecting to strava")
            print(f"response status code: {r.status_code}")

    else:
        flash("There was an issue connecting to strava")
    return redirect(url_for('profile.index'))


# function to refresh token
# assumes we've connected to strava in the past and we have a valid refresh token
def refresh_existing_token(client_id, secret, refresh_token):
    print("refreshing token")
    token_url = 'https://www.strava.com/oauth/token'
    payload = {'client_id': client_id, 'secret': secret, 'grant_type': 'refresh_token', 'refresh_token': refresh_token}
    r = requests.post(token_url, data=payload)
    if r.status_code == 200:
        bearer_token = r.json()['access_token']
        token_exp = r.json()['expires_at']
        refresh_token = r.json()['refresh_token']
        update_athlete_tokens(bearer_token, token_exp, refresh_token, True, g.athlete['id'])
        print("token refreshed")
        return True
    else:
        print(f"Something went wrong. Response: {r.status_code}")
        return False


# function to check if the user has a valid token
def has_valid_token():
    if g.athlete['connected_to_strava'] != 1:
        print(g.athlete['connected_to_strava'])
        return False
    if g.athlete['strava_bearer_token_exp'] > time.time():
        return True
    else:
        return False


def update_athlete_tokens(bearer_token, token_exp, refresh_token, connected, athlete_id):
    db = get_db()
    db.execute(
        'UPDATE athlete'
        ' SET strava_bearer_token = ?, strava_bearer_token_exp = ?, strava_refresh_token = ?, connected_to_strava = ?'
        ' WHERE id = ?',
        (bearer_token, token_exp, refresh_token, connected, athlete_id)
    )
    db.commit()


@bp.route("/pull_activity/", methods=['POST'])
def hello_world():
    client_id, secret, x, y, z, refresh_token, a = db_utils.check_prerequisites()
    valid_token = has_valid_token()
    most_recent = most_recent_activity(g.athlete['id'])
    if g.athlete['connected_to_strava'] != 1:
        flash("you must be connected to strava")
    elif not valid_token:
        print("refreshing token")
        valid_token = refresh_existing_token(client_id, secret, refresh_token)

    if valid_token:
        bearer_token = g.athlete['strava_bearer_token']
        # get the most recent activity and add it to the database
        parameters = {'per_page': 2, 'page': 1}
        if most_recent:
            parameters['after'] = most_recent
        header = {'Authorization': 'Bearer ' + bearer_token}
        base = 'https://www.strava.com/api/v3/athlete/activities'
        activities = requests.get(base, headers=header, params=parameters).json()
        added_to_db = False
        for activity in activities:
            added_to_db = added_to_db or db_utils.save_activity(activity, g.athlete['id'])
        if added_to_db:
            flash("Activity Pulled!")
        else:
            flash("No new activities to pull.")

    else:
        print(g.athlete['connected_to_strava'])
        flash("You must be connected to strava")
    return render_template('profile/index.html')


def most_recent_activity(athlete_id):
    db = get_db()
    most_recent = db.execute(
        'SELECT max(start_date) FROM activity WHERE athlete_id = ?',
        (athlete_id,)).fetchone()[0]
    if most_recent:
        epoch = datetime.strptime(most_recent, "%Y-%m-%d %H:%M:%S").timestamp()
        return epoch
    else:
        return None
