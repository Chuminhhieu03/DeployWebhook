from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import os
import base64
from dotenv import load_dotenv

# Tải các biến môi trường từ tệp .env
load_dotenv()

app = FastAPI()

# # Đường dẫn đến thư mục frontend
# app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Lấy thông tin từ biến môi trường
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Tạo biến YOUR_BASE64_ENCODED_CREDENTIALS


def get_base64_credentials(client_id: str, client_secret: str) -> str:
    credentials = f"{client_id}:{client_secret}"
    return base64.b64encode(credentials.encode()).decode()


# Sử dụng hàm để mã hóa credentials
YOUR_BASE64_ENCODED_CREDENTIALS = get_base64_credentials(
    CLIENT_ID, CLIENT_SECRET)

# Giả sử bạn lưu trữ access_token và refresh_token ở đây
ACCESS_TOKEN = None
REFRESH_TOKEN = None

# @app.get("/", response_class=HTMLResponse)
# async def read_root():
#     return HTMLResponse(open("frontend/index.html").read())

class TokenRequest(BaseModel):
    code: str

class Meeting(BaseModel):
    topic: str
    type: int
    start_time: str
    duration: int
    timezone: str
    agenda: str
    password: str = None  # Mật khẩu có thể không bắt buộc
    settings: dict = None  # Cài đặt bổ sung

# lấy token
@app.post("/oauth/token")
async def get_token(token_request: TokenRequest):
    global ACCESS_TOKEN, REFRESH_TOKEN

    code = token_request.code
    print(code)
    # Thực hiện yêu cầu để lấy Access Token và Refresh Token
    token_response = requests.post(
        "https://zoom.us/oauth/token",
        headers={
            "Authorization": f"Basic {YOUR_BASE64_ENCODED_CREDENTIALS}",
        },
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        }
    )

    if token_response.status_code == 200:
        tokens = token_response.json()
        ACCESS_TOKEN = tokens.get("access_token")
        REFRESH_TOKEN = tokens.get("refresh_token")
        return {"access_token": ACCESS_TOKEN, "refresh_token": REFRESH_TOKEN}

    raise HTTPException(status_code=token_response.status_code,
                        detail=token_response.json())

# refresh token
@app.post("/refresh_token")
async def refresh_token():
    global ACCESS_TOKEN

    # Thực hiện yêu cầu để lấy Access Token mới bằng Refresh Token
    token_response = requests.post(
        "https://zoom.us/oauth/token",
        headers={
            "Authorization": f"Basic {YOUR_BASE64_ENCODED_CREDENTIALS}",
        },
        data={
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN
        }
    )

    if token_response.status_code == 200:
        tokens = token_response.json()
        ACCESS_TOKEN = tokens.get("access_token")
        # Cập nhật refresh token mới
        REFRESH_TOKEN = tokens.get("refresh_token")
        return {"access_token": ACCESS_TOKEN, "refresh_token": REFRESH_TOKEN}

    raise HTTPException(status_code=token_response.status_code,
                        detail=token_response.json())




# lấy ra danh sách người tham gia
@app.get("/meetings/{meeting_id}/participants")
async def get_meeting_participants(meeting_id: str):
    global ACCESS_TOKEN

    # Gọi API để lấy thông tin người tham gia cuộc họp
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    response = requests.get(
        f"https://api.zoom.us/v2/meetings/{meeting_id}/participants", headers=headers)

    if response.status_code == 200:
        return response.json().get('participants', [])

    # Nếu token hết hạn, yêu cầu refresh token
    if response.status_code == 401:
        await refresh_token()  # Cập nhật access token
        return await get_meeting_participants(meeting_id)  # Thử lại lần nữa

    raise HTTPException(status_code=response.status_code,
                        detail=response.json())
