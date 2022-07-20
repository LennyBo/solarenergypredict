import sys
sys.path.append('.')  # Adds parent directory so we can import other modules
import requests
from Tools.Console import log

def make_request(url, method='GET', data=None):
    if method == 'GET':
        response = requests.get(url)
    elif method == 'POST':
        response = requests.post(url, data=data)
        
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        log("Request error: " + str(response.status_code))
