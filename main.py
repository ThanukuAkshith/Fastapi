from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, get_db,SessionLocal
from database_models import Courses, Sessions, Enrollments, Messages
from schemas import ChatRequest, ChatResponse, EnrollmentCreate, SessionCreate
from datetime import datetime

app = FastAPI(title="AI Campus Assistant Chatbot")


Base.metadata.create_all(bind=engine)



sample_courses = [
    {"code": "CS102", "name": "Python for AI", "category": "AI Fundamentals",
     "instructor": "Dr. Meera Iyer", "keywords": "python,beginner,programming,aiml"},
    {"code": "ML201", "name": "ML Fundamentals", "category": "Machine Learning",
     "instructor": "Prof. Arjun Nair", "keywords": "machine learning,ml,supervised"},
    {"code": "DL301", "name": "Deep Learning", "category": "Deep Learning",
     "instructor": "Dr. Kavita Reddy", "keywords": "deep learning,neural networks,tensorflow"},
    {"code": "NLP201", "name": "NLP Basics", "category": "NLP",
     "instructor": "Dr. Rohan Sharma", "keywords": "nlp,text,language"},
]

sessions = [
    {"id": 1, "session_id": "Eve", "user_mail": "priya@gmail.com", "started_at": "8Am"},
    {"id": 2, "session_id": "Noon", "user_mail": "rahul@gmail.com", "started_at": "12pm"},
    {"id": 3, "session_id": "Eve", "user_mail": "sneha@gmail.com", "started_at": "4pm"},
    {"id": 4, "session_id": "Noon", "user_mail": "vikram@gmail.com", "started_at": "6Am"}
]


enrollments = [
    {"id": 1, "session_id": 4, "course_code": "CS102", "student_name": "Iyer", "student_email": "Iyer@gmail.com", "enrolled_at": "Deep learning"},
    {"id": 2, "session_id": 2, "course_code": "ML201", "student_name": "Virat", "student_email": "virat@gmail.com", "enrolled_at": "python"}
]

def init_db():
    db = SessionLocal()
    course_count = db.query(Courses).count()

    if course_count == 0:
        for c in sample_courses:
            db.add(Courses(**c))
        db.commit()
        print("Database initialized with sample courses.")
    else:
        print("Courses already exist in the database.")

    db.close()

init_db()



class ChatBot:
    def detect_intent(self, message: str):
        msg = message.lower()
        if "hi" in msg or "hello" in msg:
            return "greeting"
        elif "list" in msg or "show" in msg:
            return "list_courses"
        elif "enroll" in msg:
            return "enroll"
        elif any(k in msg for k in ["python", "ml", "deep learning", "nlp"]):
            return "search_course"
        elif "bye" in msg:
            return "exit"
        else:
            return "unknown"

    def find_courses(self, db, keyword):
        keyword = keyword.lower()
        courses = db.query(Courses).all()
        found = []
        for course in courses:
            if keyword in course.keywords.lower():
                found.append(f"{course.code} - {course.name} ({course.instructor})")
        if len(found) > 0:
            return "\n".join(found)
        else:
            return "No matching courses found."


    def process_message(self, db, message: str):
        intent = self.detect_intent(message)

        if intent == "greeting":
            return "Hello! I can help you explore AI/ML courses.", intent

        elif intent == "list_courses":
            courses = db.query(Courses).all()
            names_list = []
            for c in courses:
                names_list.append(c.name)
            names = ", ".join(names_list)
            return f"Available courses: {names}", intent

        elif intent == "search_course":
            return self.find_courses(db, message), intent

        elif intent == "enroll":
            return "To enroll, please provide your course code and details.", intent

        elif intent == "exit":
            return "Goodbye! Have a great day!", intent

        else:
            return "Sorry, I didn't understand that.", intent



@app.get("/")
def home():
    return {"message": "Welcome to AI Campus Assistant Chatbot"}

@app.post("/session")
def create_session(request: SessionCreate, db: Session = Depends(get_db)):
    existing = db.query(Sessions).filter(Sessions.session_id == request.session_id).first()
    if existing:
        return {"message": "Session already exists."}
    session = Sessions(session_id=request.session_id, user_email=request.user_email)
    db.add(session)
    db.commit()
    return {"message": "New session started."}

@app.get("/courses")
def get_courses(db: Session = Depends(get_db)):
    return db.query(Courses).all()

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    bot = ChatBot()
    response, intent = bot.process_message(db, request.user_message)

  
    chat_msg = Messages(
        session_id=request.session_id,
        user_message=request.user_message,
        bot_response=response,
        intent=intent,
        
    )
    db.add(chat_msg)
    db.commit()
    return ChatResponse(bot_response=response, intent=intent)

@app.post("/enroll")
def enroll(request: EnrollmentCreate, db: Session = Depends(get_db)):
    course = db.query(Courses).filter(Courses.code == request.course_code).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    enrollment = Enrollments(
        session_id=request.session_id,
        student_email=request.student_email,
        student_name=request.student_name,
        course_code=request.course_code,
        
    )
    db.add(enrollment)
    db.commit()
    return {"message": f"Enrolled successfully in {course.name}!"}

@app.get("/courses/search")
def search_courses(keyword: str, db: Session = Depends(get_db)):
    keyword = keyword.lower()
    courses = db.query(Courses).all()
    found = []
    for c in courses:
        if keyword in c.keywords.lower() or keyword in c.name.lower():
            found.append(c)
    if len(found) == 0:
        raise HTTPException(status_code=404, detail="No courses found matching that keyword.")

    result = []
    for c in found:
        course_data = {
            "code": c.code,
            "name": c.name,
            "category": c.category,
            "instructor": c.instructor,
            "keywords": c.keywords
        }
        result.append(course_data)

    return result

@app.get("/enrollments")
def get_enrollments(db: Session = Depends(get_db)):
    return db.query(Enrollments).all()


@app.get("/chat-history")
def chat_history(email: str, db: Session = Depends(get_db)):
    sessions = db.query(Sessions).filter(Sessions.user_email == email).all()
    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions found for this email.")
    messages = []
    for s in sessions:
        chats = db.query(Messages).filter(Messages.session_id == s.session_id).all()
        for c in chats:
            messages.append({
                "session_id": s.session_id,
                "user_message": c.user_message,
                "bot_response": c.bot_response,
                "intent": c.intent,
                "created_at": c.created_at
            })
    return messages
