from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Participant(BaseModel):
    name: str
    email: str

class MeetingLog(BaseModel):
    start_time: datetime
    end_time: datetime
    participants: List[Participant]
    status: str
    notes: Optional[str] = None