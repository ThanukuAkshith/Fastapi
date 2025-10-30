from pydantic import BaseModel
from typing import List, Optional



class ChatRequest(BaseModel):
    session_id: str
    user_message: str

class ChatResponse(BaseModel):
    bot_response: str
    intent: str

class SessionCreate(BaseModel):
    session_id: str
    user_email: Optional[str] = None  

class EnrollmentCreate(BaseModel):
    session_id: str
    student_email: str
    student_name: str
    course_code: str


class CourseSchema(BaseModel):
    id: int
    code: str
    name: str
    category: str
    instructor: str
    keywords: List[str]


class SessionSchema(BaseModel):
    id: int
    session_id: int
    user_email: str
    started_at: str




class EnrollmentSchema(BaseModel):
    id: int
    session_id: int
    course_code: str
    student_name: str
    student_email: str
    enrolled: str

class ChatMessageSchema(BaseModel):
    id: int
    session_id: int
    user_message: str
    bot_response: str
    intent: str
    created_at: str