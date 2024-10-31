from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
import requests
import os
import base64
from urllib.parse import quote
from fastapi.websockets import WebSocket, WebSocketDisconnect

# import url
from api.url import router as api_url
from webhooks.webhook import webhook_router
templates = Jinja2Templates(directory="GUI/templates")
# Mount the static files directory

app = FastAPI()
app.mount("/static", StaticFiles(directory="GUI/static"), name="static")
app.include_router(api_url)
app.include_router(webhook_router)

CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
REDIRECT_URI = os.getenv("ZOOM_REDIRECT_URI")
credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
ENCODE_CREDENTIAL = base64.b64encode(credentials.encode()).decode("utf-8")

# render template
@app.get("/home")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


class TokenRequest(BaseModel):
    code: str

@app.get("/login")
async def login():
    redirect_uri = quote(REDIRECT_URI, safe="")
    zoom_auth_url = f"https://zoom.us/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={redirect_uri}"
    return RedirectResponse(url=zoom_auth_url)

@app.get("/oauth/callback")
async def oauth_callback(request: Request,code: str):
    token_response = requests.post(
        "https://zoom.us/oauth/token",
        headers={
            "Authorization": f"Basic {ENCODE_CREDENTIAL}",
        },
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        }
    )
    if token_response.status_code == 200:
        tokens = token_response.json()
        access_token = tokens.get("access_token")
        return templates.TemplateResponse("meeting_url_form.html", {"request": request, "access_token": access_token})

@app.post("/start_meeting")
async def start_meeting(request: Request):
    form = await request.form()
    access_token = form.get("access_token")
    meeting_url = form.get("meeting_url")
    return templates.TemplateResponse("meeting_history.html", {"request": request, "meeting_url": meeting_url})

websocket_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)