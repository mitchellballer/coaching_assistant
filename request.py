import requests
import json
import properties
import time
import configparser

from urllib.parse import urlparse, parse_qs
from requests.compat import urljoin

from requests.exceptions import HTTPError
from requests_oauthlib import OAuth2Session

#pull in properties from config file
config = configparser.ConfigParser()
config_file = 'config.properties'
config.read(config_file)
bearer_token = config['TOKEN']['bearer_token']
bearer_token_expiration = config['TOKEN']['bearer_token_expiration']
refresh_token = config['TOKEN']['refresh_token']

#not sure if I need to do this. But since we compare to an int later it might be the safe thing to do
if bearer_token_expiration == '':
    bearer_token_expiration = 0
else:
    bearer_token_expiration = int(bearer_token_expiration)

client_id = config['CLIENT']['client_id']
client_secret = config['CLIENT']['client_secret']
redirect_uri = 'http://localhost/exchange_token'
scope = 'activity:read'
kwargs = {'approval_prompt': 'force'}
approval_prompt = 'force'
auth_url = 'https://www.strava.com/oauth/authorize'
token_url = 'https://www.strava.com/oauth/token'
curr_time = time.time()

#if don't yet have a bearer token or refresh token, get them both
if bearer_token == '' or refresh_token == '':
    oauth = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, scope=[scope])
    authorization_url, state = oauth.authorization_url(auth_url)

    #unable to get **kwargs to accept strava's 'approval_prompt' arg.
    # So just tack it on the end here.
    #Authorization url still messes with symbols in redirect_uri but it seems to be functional
    authorization_url = authorization_url + '&approval_prompt=force'

    print ("Please go to " + authorization_url + " and authorize access.")
    authorization_response = input('Enter the full callback URL: ')

    #take response, parse out code if we got one
    o = urlparse(authorization_response)
    query = parse_qs(o.query)
    if 'code' in query:
        authorization_code = query['code']
        
    else:
        print ("No authorization code")

    #perform token exchange using auth code
    payload = {'client_id':client_id, 'client_secret': client_secret, 'code': authorization_code, 'grant_type': 'authorization_code'}
    r = requests.post(token_url, data=payload)

    if r.status_code == 200:
        #save our new token to properties file and update the expiration
        bearer_token = r.json()['access_token']
        bearer_token_expiration = r.json()['expires_at']
        refresh_token = r.json()['refresh_token']
        config['TOKEN']['bearer_token'] = bearer_token
        config['TOKEN']['bearer_token_expiration'] = str(bearer_token_expiration)
        config['TOKEN']['refresh_token'] = refresh_token
        with open(config_file, 'w') as new_config:
            config.write(new_config)

#if we've already received a short term token but it's expired, we should refresh
elif bearer_token_expiration < curr_time:
    payload = {'client_id':client_id,'client_secret': client_secret,'grant_type':'refresh_token','refresh_token':refresh_token}
    r = requests.post(token_url,data=payload)
    #successful response: {"token_type":"Bearer","access_token":"asdf1234","expires_at":123445,"expires_in":21600,"refresh_token":"asdf1234"}
    if r.status_code == 200:
        bearer_token = r.json()['access_token']
        bearer_token_expiration = r.json()['expires_at']
        refresh_token = r.json()['refresh_token']
        config['TOKEN']['bearer_token'] = bearer_token
        config['TOKEN']['bearer_token_expiration'] = str(bearer_token_expiration)
        config['TOKEN']['refresh_token'] = refresh_token
        with open(config_file, 'w') as new_config:
            config.write(new_config)
#let's get activities from the past week
#url requires epoch time
before= time.time()
#one week ago was 60*60*24*7 seconds ago
after = before - (60*60*24*7)
page=1
per_page=10
base = 'https://www.strava.com/api/v3/athlete/activities'
args = '?before='+str(before)+'&after='+str(after)+'&page='+str(page)+'&per_page='+str(per_page)
#parameters = {'before': str(before), 'after': str(after), 'page':str(page), 'per_page':str(per_page)}
parameters = {'per_page':20, 'page':1}
bearer = 'Bearer '+ bearer_token
header = {'Authorization': 'Bearer ' + bearer_token}

activitiesURL = urljoin(base,args)
#this is our list of 20 activities.
activities = requests.get(base, headers=header,params=parameters).json()
for i in activities:
    print(i['name'])

#"https://www.strava.com/api/v3/athlete/activities?before=&after=&page=&per_page=" "Authorization: Bearer [[token]]"


