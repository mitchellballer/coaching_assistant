from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import properties
import configparser

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
    if request.method == 'POST':
        strava_id = request.form['strava_id']
        error = None
        if not strava_id:
            error = 'Strava id is required'
        elif not strava_id.isdigit():
            error = 'your strava ID is a number'
        if error is not None:
            flash(error)
            return redirect(url_for('profile.index'))
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
    if strava_id == None:
        return render_template('profile/connect.html')
    
    #put code to connect to strava here
    print('connecting to strava')
    print('redirecting to profile page')
    return redirect(url_for('profile.index'))

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
