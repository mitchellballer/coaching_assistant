from flask import flash, request, g
from flaskr.db import get_db
from urllib.parse import urlparse, parse_qs
from . import strava_utils

import time
import requests


def exchange_token():
    print("starting exchange token function")
    token_url = 'https://www.strava.com/oauth/token'
    client_id, secret = strava_utils.check_prerequisites()
    print(client_id)
    print(secret)

    if request.method == 'GET':
        authorization_response = request.url
        o = urlparse(authorization_response)
        query = parse_qs(o.query)
        if 'code' in query:
            authorization_code = query['code'][0]
            print(f"authorization code: {authorization_code}")
        else:
            print("No authorization code")
        # perform token exchange
        payload = {'client_id': client_id, 'client_secret': secret, 'code': authorization_code, 'grant_type': 'authorization_code'}
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
            print(f"more info? {r.text}")

    else:
        flash("There was an issue connecting to strava")
        print(request.data)


# function to refresh token
# assumes we've connected to strava in the past and we have a valid refresh token
def refresh_existing_token(client_id, secret, refresh_token):
    print("refreshing token")
    token_url = 'https://www.strava.com/oauth/token'
    payload = {'client_id': client_id, 'client_secret': secret, 'grant_type': 'refresh_token', 'refresh_token': refresh_token}
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
    if g.athlete['strava_bearer_token_expiration'] > time.time():
        return True
    else:
        return False


def update_athlete_tokens(bearer_token, token_exp, refresh_token, connected, athlete_id):
    db = get_db()
    db.execute(
        'UPDATE athlete'
        ' SET strava_bearer_token = ?, strava_bearer_token_expiration = ?, strava_refresh_token = ?, connected_to_strava = ?'
        ' WHERE id = ?',
        (bearer_token, token_exp, refresh_token, connected, athlete_id)
    )
    db.commit()
