def exchange_token(client_id, client_secret, athlete_id, bearer_token, token_expiration, refresh_token, strava_id):
    token_url = 'https://www.strava.com/oauth/token'
    print("starting exchange token function")
