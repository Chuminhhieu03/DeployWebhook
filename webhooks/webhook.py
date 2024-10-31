from fastapi import APIRouter, Request, HTTPException, Header
import json
import secrets
import hmac
import hashlib
import os
from dotenv import load_dotenv
import datetime
import paho.mqtt.client as mqtt

load_dotenv()

webhook_router = APIRouter()

MQTT_BROKER = os.environ.get('MQTT_BROKER')  
MQTT_PORT = int(os.environ.get("MQTT_PORT"))               
MQTT_USERNAME = os.environ.get('MQTT_USERNAME')  
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD') 
print(MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD)
client = mqtt.Client()

client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
print(f"Đã kết nối tới MQTT broker: {MQTT_BROKER}")

ZOOM_SECRET_TOKEN = os.environ.get("SECRET_TOKEN")

@webhook_router.post("/webhook")
async def webhook(request: Request):
    # print(ZOOM_SECRET_TOKEN)
    headers = dict(request.headers)
    body = await request.json()
    # print(headers)
    print("Body", body)

    if 'payload' in body and 'plainToken' in body['payload']: # Dùng để validated url trên link zoom webhook
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
    event = body.get('event')
    print(payload)
    print(event)
    object_payload = payload['object']
    print(object_payload)
    participant = object_payload['participant']
    name = participant['user_name']
    
    if event == 'meeting.participant_joined':
        topic = 'zoom/participant/joined'
        if payload:
            joined_time = participant['join_time']
            timestamp = datetime.datetime.fromisoformat(joined_time.replace("Z", "+00:00"))
            utc_plus_7 = timestamp + datetime.timedelta(hours=7)
            formatted_timestamp = utc_plus_7.strftime("[%d-%m-%Y %H:%M:%S]")
            send_data = {"message": formatted_timestamp + " " + name + " đã tham gia cuộc họp"}
            client.publish(topic, json.dumps(send_data))
            print(f"Đã gửi dữ liệu tới {topic}: {payload}")
    elif event == 'meeting.participant_left':
        topic = 'zoom/participant/left'
        if payload:
            client.publish(topic, json.dumps(payload))
            print(f"Đã gửi dữ liệu tới {topic}: {payload}")
