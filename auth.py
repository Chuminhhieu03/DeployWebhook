import requests
import base64
from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.environ.get('ZOOM_CLIENT_ID')
client_secret = os.environ.get('ZOOM_CLIENT_SECRET')
account_id = os.environ.get('ZOOM_ACCOUNT_ID')

def get_token():
    token_url = "https://zoom.us/oauth/token"

    auth_string = f"{client_id}:{client_secret}"
    b64_auth_string = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth_string}",
    }

    payload = {
        "grant_type": "account_credentials",
        "account_id": account_id
    }
    
    response = requests.post(token_url, headers=headers, data=payload)
    if response.status_code == 200:
        token_data = response.json()['access_token']
        return token_data
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")