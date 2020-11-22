from flask import (
    Blueprint, flash, g, redirect, render_template, url_for
)
from flaskr.auth import login_required
from flaskr.db import get_db
from datetime import datetime
from requests_oauthlib import OAuth2Session
from .utils import token_utils, strava_utils

import requests
import time

bp = Blueprint('profile', __name__)


@bp.route('/profile')
@login_required
def index():
    return render_template('profile/index.html')


@bp.route('/authorized/')
def authorized():
    return redirect(url_for('profile.index'))


@bp.route('/connect', methods=('GET', 'POST'))
@login_required
def connect():
    print('gathering prerequisites')

    client_id, secret = strava_utils.check_prerequisites()
    bearer_token = g.athlete['strava_bearer_token']
    token_exp = g.athlete['strava_bearer_token_expiration']
    refresh_token = g.athlete['strava_refresh_token']

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
        token_utils.refresh_existing_token(client_id, secret, refresh_token)

    print('redirecting to profile page')
    return redirect(url_for('profile.index'))


@bp.route('/exchange_token', methods=('GET', 'POST'))
def exchange_token():
    token_utils.exchange_token()
    return redirect(url_for('profile.index'))


@bp.route("/pull_activity/", methods=['POST'])
def hello_world():
    client_id, secret = strava_utils.check_prerequisites()
    valid_token = token_utils.has_valid_token()
    most_recent = most_recent_activity(g.athlete['id'])
    refresh_token = g.athlete['strava_refresh_token']
    if g.athlete['connected_to_strava'] != 1:
        flash("you must be connected to strava")
    elif not valid_token:
        print("refreshing token")
        valid_token = token_utils.refresh_existing_token(client_id, secret, refresh_token)

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
            added_to_db = added_to_db or strava_utils.save_activity(activity, g.athlete['id'])
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
