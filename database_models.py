from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Courses(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    category = Column(String)
    instructor = Column(String)
    keywords = Column(String)

class Sessions(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String)
    user_email = Column(String)
    started_at = Column(String)

class Enrollments(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer)
    course_code = Column(String, ForeignKey("courses.code"))
    student_name = Column(String)
    student_email = Column(String)

class Messages(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String)
    user_message = Column(String)
    bot_response = Column(String)
    intent = Column(String)
    created_at = Column(String)
