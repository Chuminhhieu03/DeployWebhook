from pydantic import BaseModel
import datetime


class CreateMeetingRequest(BaseModel):
    topic: str
    type: int
    start_time: str
    duration: int
    timezone: str
    agenda: str
    password: str = None  # Mật khẩu có thể không bắt buộc
    settings: dict = None  # Cài đặt bổ sung
    invitees: list = None  # Danh sách email mời
