from fastapi import APIRouter, HTTPException, Depends
import requests
from common.auth import get_token
from http_request.meeting import CreateMeetingRequest

router = APIRouter()


@router.get("/meetings/users/{user_id}/{typeList}", summary="Get meeting list by user's id")
async def get_meeting_list(user_id: str, typeList: str, ACCESS_TOKEN: str = Depends(get_token)):
    # Gọi API để lấy danh sách cuộc họp
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    response = requests.get(
        f"https://api.zoom.us/v2/users/{user_id}/meetings", headers=headers, params={"type": typeList})

    if response.status_code == 200:
        return response.json().get('meetings', [])

    # Nếu token hết hạn, yêu cầu refresh token
    # if response.status_code == 401:
    #     await refresh_token()  # Gọi hàm refresh_token để cập nhật access token
    #     return await get_meeting_list(user_id)  # Thử lại lần nữa

    raise HTTPException(status_code=response.status_code,
                        detail=response.json())


@router.get("/meetings/{meeting_id}", summary="Get a meeting by meeting's id")
async def get_meeting_list(meeting_id: str, ACCESS_TOKEN: str = Depends(get_token)):
    # Gọi API để lấy danh sách cuộc họp
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    response = requests.get(
        f"https://api.zoom.us/v2/meetings/{meeting_id}", headers=headers)

    if response.status_code == 200:
        return response.json()

    # Nếu token hết hạn, yêu cầu refresh token
    # if response.status_code == 401:
    #     await refresh_token()  # Gọi hàm refresh_token để cập nhật access token
    #     return await get_meeting_list(user_id)  # Thử lại lần nữa

    raise HTTPException(status_code=response.status_code,
                        detail=response.json())


# tạo cuộc họp
@router.post("/meetings", summary="Create a meeting")
async def create_meeting(meeting: CreateMeetingRequest, ACCESS_TOKEN: str = Depends(get_token)):
    # Gọi API để tạo cuộc họp
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.zoom.us/v2/users/me/meetings", headers=headers, json=meeting.dict())

    if response.status_code == 201:
        meeting_info = response.json()
        contentAfterAddRegistrants = ""
    # # Nếu token hết hạn, yêu cầu refresh token
    # if response.status_code == 401:
    #     await refresh_token()  # Cập nhật access token
    #     return await create_meeting(meeting)  # Thử lại lần nữa
        if meeting.invitees:
            contentAfterAddRegistrants = add_registrants(
                meeting_info["id"], meeting.invitees, ACCESS_TOKEN)
        meeting_info["contentAfterAddRegistrants"] = contentAfterAddRegistrants
        return meeting_info

    raise HTTPException(status_code=response.status_code,
                        detail=response.json())


def extract_name_from_email(email: str):
    # Giả sử email có định dạng: firstname.lastname@example.com
    name_part = email.split('@')[0]

    # Tách phần name dựa vào dấu chấm (nếu có)
    name_split = name_part.split('.')

    if len(name_split) == 2:
        first_name, last_name = name_split[0].capitalize(
        ), name_split[1].capitalize()
    else:
        # Nếu không có dấu chấm, dùng toàn bộ làm first_name và để last_name trống
        first_name = name_split[0].capitalize()
        last_name = ""

    return first_name, last_name


def add_registrants(meeting_id: str, email_list: list, ACCESS_TOKEN: str):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    content = ""

    for email in email_list:
        # Lấy first_name và last_name từ email
        first_name, last_name = extract_name_from_email(email)

        data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name
        }

        registrant_response = requests.post(
            f"https://api.zoom.us/v2/meetings/{meeting_id}/registrants", headers=headers, json=data)
        print(registrant_response.json())
        if registrant_response.status_code != 200:
            content += f"Không mời được người dùng có email: {email}\n"
        else:
            content += f"Đã mời người dùng có email: {email}\n"
    return content
