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
    
# def refresh_token():
    
#     ACCESS_TOKEN = get_token()

#     auth_string = f"{client_id}:{client_secret}"
#     b64_auth_string = base64.b64encode(auth_string.encode()).decode()

#     # Thực hiện yêu cầu để lấy Access Token mới bằng Refresh Token
#     token_response = requests.post(
#         "https://zoom.us/oauth/token",
#         headers={
#             "Authorization": f"Basic {b64_auth_string}",
#         },
#         data={
#             "grant_type": "refresh_token",
#             "refresh_token": REFRESH_TOKEN
#         }
#     )

#     if token_response.status_code == 200:
#         tokens = token_response.json()
#         ACCESS_TOKEN = tokens.get("access_token")
#         # Cập nhật refresh token mới
#         REFRESH_TOKEN = tokens.get("refresh_token")
#         return {"access_token": ACCESS_TOKEN, "refresh_token": REFRESH_TOKEN}

#     return (status_code=token_response.status_code,
#                         detail=token_response.json())