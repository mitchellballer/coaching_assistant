import requests
import json
import properties

from requests.exceptions import HTTPError
from requests_oauthlib import OAuth2Session

""" url = 'https://www.strava.com/api/v3/athlete'
data = {'before': '56','after': '56', 'page': '1', }
cert = "Bearer: %s" % (properties.token)
print (cert)

try:
    response = requests.get(url, headers = {"Authorization": cert})
    #response = requests.get(url, auth = ('Authorization', cert))
    #response = requests.get('https://api.github.com')
    #response = requests.get('https://api.github.com/invalid')

    #raise Exception if response not successful
    response.raise_for_status()

except HTTPError as http_err:
    print('HTTP error occurred: {http_err}', http_err)
except Exception as err:
    print('Other error occurred: {err}')
else:
    print('Success!') """

#response body, stored in dictionary
#payload = json.loads(response.content)

#headers, stored in dictionary
#headers = response.headers

#params = {'client_id': properties.client_id, 'response_type': 'code', 'redirect_uri': redirect_uri}

client_id = properties.client_id
client_secret = properties.client_secret
redirect_uri = 'http://localhost/exchange_token'
scope = 'read'
kwargs = {'approval_prompt': 'force'}
approval_prompt = 'force'
auth_url = 'https://www.strava.com/oauth/authorize'

oauth = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, scope=[scope])
authorization_url, state = oauth.authorization_url(auth_url)

#unable to get **kwargs to accept strava's 'approval_prompt' arg. So we literally just tack it on the end here.
authorization_url = authorization_url + '&approval_prompt=force'

print 'Please go to %s and authorize access.' % authorization_url
authorization_response = raw_input('Enter the full callback URL: ')


"""
oauth.authorization_url returns this url:
https://www.strava.com/oauth/authorize?response_type=code&client_id=41250&redirect_uri=http%3A%2F%2Flocalhost%2Fexchange_token%26approval_prompt%3Dforce%26scope%3Dread&state=lMpp5o30GyPKst2TZ43HtZGvTAl0bE 
    generates: http://localhost/exchange_token&approval_prompt=force&scope=read?state=OL8HF4OQRLYTVsGwCfOMgIjcqbYPeA&code=7c08804ea78bbc15001ece4cb66917949cfa264f&scope=

However, that messed up redirect_uri doesn't work. If I substitute the non messed up uri as below, it correctly routes me in the browser.
https://www.strava.com/oauth/authorize?response_type=code&client_id=41250&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=read 
    generates: http://localhost/exchange_token?state=&code=dba82bf737629169d54b35d2386e0d2a1a48763a&scope=read

"""