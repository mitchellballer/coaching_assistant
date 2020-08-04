from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import properties
import configparser
import requests
import time
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
    
    #if we already have a short term token but it's expired, we should refresh
    elif token_expiration < time.time():
        print('refresh short term token')
    
    #get the most recent activity and add it to the database 
    parameters = {'per_page':1, 'page':1}
    header = {'Authorization':'Bearer ' + bearer_token}
    base = 'https://www.strava.com/api/v3/athlete/activities'
    activity = requests.get(base, headers=header,params=parameters).json()[0]

    print(activity['name'])
    print(activity['start_date'])
    save_activity(activity, g.athlete['id'])

    print('redirecting to profile page')
    return redirect(url_for('profile.index'))

#save given activity to database for given athlete
#input is a single activity in json form provided by strava
def save_activity(activity, athlete_id):
    title = activity['name']
    #TODO fix this so our timestamp/datetimes are compatible 
    #this is a terrible hack solution
    #strava gives us datetime in format: 2018-02-20T18:02:13Z
    #flask at somepoint splits this into two strings by a string separating date from time and we can't have a z at the end...
    start = activity['start_date'].replace('T', ' ').replace('Z','')
    description = 'sample description'#activity['description']
    distance = activity['distance']
    duration = activity['elapsed_time']
    #TODO might need to add strava_id or something to activity database so we don't add duplicates
    db = get_db()
    db.execute(
        'INSERT INTO activity (start_date, title, description, distance, duration, athlete_id)'
        ' VALUES (?, ?, ?, ?, ?, ?)',
        (start, title, description, distance, duration, athlete_id)
    )
    db.commit()



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
