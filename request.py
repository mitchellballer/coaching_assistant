import requests
import json
import properties

from requests.exceptions import HTTPError

print (properties.token)

try:
    response = requests.get('https://api.github.com')
    #response = requests.get('https://api.github.com/invalid')

    #raise Exception if response not successful
    response.raise_for_status()
except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}')
else:
    print('Success!')

#response body, stored in dictionary
payload = json.loads(response.content)

#headers, stored in dictionary
headers = response.headers
