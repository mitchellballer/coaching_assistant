from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import properties
import configparser
import requests
from urllib.parse import urlparse, parse_qs

from requests_oauthlib import OAuth2Session

bp = Blueprint('profile', __name__)

@bp.route('/profile')
@login_required
def index():
    return render_template('profile/index.html')

@bp.route('/connect', methods=('GET','POST'))
@login_required
def connect():
    print('gathering prerequisites')

    client_id, client_secret, athlete_id, bearer_token, token_expiration, refresh_token, strava_id = check_prerequisites()
    
    #If they're submitting their strava ID now, make sure it seems correct then add to database
    if request.method == 'POST':
        strava_id = request.form['strava_id']
        error = None
        if not strava_id:
            error = 'Strava id is required'
        elif not strava_id.isdigit():
            error = 'your strava ID is a number'
        if error is not None:
            flash(error)
            return redirect(url_for('profile.connect'))
        strava_id = int(strava_id)
        db = get_db()
        db.execute(
            'UPDATE athlete'
            ' SET strava_athlete_id = ?'
            ' WHERE id = ?',
            (strava_id, g.athlete['id'])
        )
        db.commit()


    #if strava_id is none, they need to add it to database before we can connect.
    #So we redirect them to the connect page where they can enter it.
    if strava_id == None:
        return render_template('profile/connect.html')
    
    #put code to connect to strava here
    print('connecting to strava')
    print_current_state()
    
    #TODO get this redirecting to a page where we can use without the command line
    redirect_uri = 'http://localhost:5000/exchange_token'
    auth_url = 'https://www.strava.com/oauth/authorize'
    token_url = 'https://www.strava.com/oauth/token'
    scope = 'activity:read'

    #if we don't have a bearer token or refresh token, get them.
    if bearer_token == None or refresh_token == None:
        oauth = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, scope=[scope])
        authorization_url, state = oauth.authorization_url(auth_url)
        authorization_url = authorization_url + '&approval_prompt=force'
        print("Please go to "+authorization_url+" and authorize access.")
        authorization_response = input('Enter the full callback URL: ')

        #parse response code if we got one
        o = urlparse(authorization_response)
        query = parse_qs(o.query)
        if 'code' in query:
            authorization_code = query['code']

        else:
            print("No authorization code")

        #perform token exchange using auth code
        payload = {'client_id':client_id, 'client_secret': client_secret, 'code': authorization_code, 'grant_type': 'authorization_code'}
        r = requests.post(token_url, data=payload)

        #if success, save our new token and update expiration
        if r.status_code == 200:
            bearer_token = r.json()['access_token']
            token_expiration = r.json()['expires_at']
            refresh_token = r.json()['refresh_token']
            update_athlete_tokens(bearer_token, token_expiration, refresh_token, g.athlete['id'])

    print_current_state()

    print('redirecting to profile page')
    return redirect(url_for('profile.index'))

#function that just prints current info about our athlete, state of tokens etc.
def print_current_state():
    print("Printing current state")
    print(f"Athlete id: {g.athlete['id']}")
    print(f"strava bearer token: {g.athlete['strava_bearer_token']}")
    print(f"strava bearer token expiration: {g.athlete['strava_bearer_token_expiration']}")
    print(f"strava refresh token: {g.athlete['strava_refresh_token']}")
    print(f"strava athlete id: {g.athlete['strava_athlete_id']}")


def update_athlete_tokens(bearer_token, token_expiration, refresh_token, athlete_id):
    db = get_db()
    db.execute(
        'UPDATE athlete'
        ' SET strava_bearer_token = ?, strava_bearer_token_expiration = ?, strava_refresh_token = ?'
        ' WHERE id = ?',
        (bearer_token, token_expiration, refresh_token, athlete_id)
    )
    db.commit()

def check_prerequisites():
    #load client properties from config.properties
    config = configparser.ConfigParser()
    config_file = 'config.properties'
    config.read(config_file)
    client_id = config['CLIENT']['client_id']
    client_secret = config['CLIENT']['client_secret']
    #make sure we found client properties
    error = None

    if not client_id:
        error = 'No client id. Please load client ID into config.properties on the server'
    if not client_secret:
        error = 'No client secret. Please load client ID into config.properties on the server'
    if error is not None:
        flash(error)
    
    #load athlete properties from session
    athlete_id = g.athlete['id']
    bearer_token = g.athlete['strava_bearer_token']
    token_expiration = g.athlete['strava_bearer_token_expiration']
    refresh_token = g.athlete['strava_refresh_token']
    strava_id = g.athlete['strava_athlete_id']

    return client_id, client_secret, athlete_id, bearer_token, token_expiration, refresh_token, strava_id
