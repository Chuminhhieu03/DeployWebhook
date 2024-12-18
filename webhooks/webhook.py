from fastapi import APIRouter, Request, HTTPException, Header
import json
import secrets
import hmac
import hashlib
import os
from dotenv import load_dotenv
import datetime
import time
from fastapi.websockets import WebSocket, WebSocketDisconnect

load_dotenv()

webhook_router = APIRouter()


ZOOM_SECRET_TOKEN = os.environ.get("SECRET_TOKEN")

websocket_connections = []
connections = {}
event_cache = {}


@webhook_router.post("/webhook")
async def webhook(request: Request):
    # print(ZOOM_SECRET_TOKEN)
    global event_cache
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

    event_ts = body.get("event_ts")

    if event_ts in event_cache:
        print("Sự kiện đã nhận trước đó, bỏ qua...")
        return {"message": "Event already processed"}
    
    event_cache[event_ts] = time.time()

    payload = body.get('payload')
    meeting_id = payload.get("object", {}).get("id")
    event = body.get('event')
    print(payload)
    print(connections)
    
    # Xác định đối tượng chính từ payload
    object_payload = payload.get('object', {})
    participant = object_payload.get('participant', {})
    name = participant.get('user_name', 'Người dùng')

    # Lấy thời gian hiện tại và format để sử dụng cho tất cả sự kiện
    current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
    formatted_timestamp = current_time.strftime("[%d-%m-%Y %H:%M:%S]")

    # Xử lý các sự kiện
    send_data = {}
    if event == 'meeting.started':
        send_data = {"message": f"{formatted_timestamp} Cuộc họp đã bắt đầu."}
    elif event == 'meeting.ended':
        send_data = {"message": f"{formatted_timestamp} Cuộc họp đã kết thúc."}
    elif event == 'meeting.participant_joined':
        send_data = {"message": f"{formatted_timestamp} {name} đã tham gia cuộc họp."}
    elif event == 'meeting.participant_left':
        send_data = {"message": f"{formatted_timestamp} {name} đã rời khỏi cuộc họp."}

    if meeting_id not in connections:
            connections[meeting_id] = []

    # Gửi dữ liệu tới các kết nối WebSocket nếu tồn tại
    if send_data and meeting_id in connections:
        for connection in connections[meeting_id]:  
            await connection.send_text(json.dumps(send_data, ensure_ascii=False))

    event_cache = {k: v for k, v in event_cache.items() if time.time() - v < 60}
    return {"message": "Event processed successfully"}

@webhook_router.websocket("/ws/{meeting_id}")
async def websocket_endpoint(websocket: WebSocket, meeting_id: str):
    await websocket.accept()
    # Tạo danh sách kết nối nếu chưa tồn tại cho meeting_id
    if meeting_id not in connections:
        connections[meeting_id] = []
    connections[meeting_id].append(websocket)
    
    try:
        while True:
            await websocket.receive_text()  # Duy trì kết nối
    except WebSocketDisconnect:
        # Xóa kết nối khi ngắt kết nối
        connections[meeting_id].remove(websocket)

