from fastapi import APIRouter, Request, HTTPException, Header
import json
import secrets
import hmac
import hashlib
import os
from dotenv import load_dotenv
import datetime
import paho.mqtt.client as mqtt
from fastapi.websockets import WebSocket, WebSocketDisconnect

load_dotenv()

webhook_router = APIRouter()


ZOOM_SECRET_TOKEN = os.environ.get("SECRET_TOKEN")

websocket_connections = []
connections = {}


@webhook_router.post("/webhook")
async def webhook(request: Request):
    # print(ZOOM_SECRET_TOKEN)
    headers = dict(request.headers)
    body = await request.json()
    # print(headers)
    print("Body", body)

    # Dùng để validated url trên link zoom webhook
    if 'payload' in body and 'plainToken' in body['payload']:
        secret_token = ZOOM_SECRET_TOKEN.encode("utf-8")
        plaintoken = body['payload']['plainToken']
        mess = plaintoken.encode("utf-8")
        has = hmac.new(secret_token, mess, hashlib.sha256).digest()
        hexmessage = has.hex()

        response = {
            'message': {
                'plainToken': plaintoken,
                'encryptedToken': hexmessage
            }
        }
        print(response['message'])
        return response['message']

    payload = body.get('payload')
    meeting_id = payload.get("object", {}).get("id")
    event = body.get('event')
    print(payload)
    print(event)
    print(meeting_id)
    print(connections)
    object_payload = payload.get('object', {})

    participant = object_payload['participant']
    name = participant['user_name']

    if event == 'meeting.participant_joined':
        if payload:
            joined_time = participant['join_time']
            timestamp = datetime.datetime.fromisoformat(
                joined_time.replace("Z", "+00:00"))
            utc_plus_7 = timestamp + datetime.timedelta(hours=7)
            formatted_timestamp = utc_plus_7.strftime("[%d-%m-%Y %H:%M:%S]")
            send_data = {"message": formatted_timestamp +
                         " " + name + " đã tham gia cuộc họp"}
            # Ensure there is a list for this meeting_id
            if meeting_id not in connections:
                connections[meeting_id] = []
                
            for connection in connections[meeting_id]:
                await connection.send_text(json.dumps(send_data))
    elif event == 'meeting.participant_left':
        if meeting_id in connections:
            for connection in connections[meeting_id]:
                await connection.send_text(json.dumps(payload))


@webhook_router.websocket("/ws/{meeting_id}")
async def websocket_endpoint(websocket: WebSocket, meeting_id: str):
    await websocket.accept()
    # Add WebSocket connection to the meeting-specific list
    if meeting_id not in connections:
        connections[meeting_id] = []
    connections[meeting_id].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process incoming data if needed
    except WebSocketDisconnect:
        connections[meeting_id].remove(websocket)
