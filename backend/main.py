from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import jwt

#config
DATABASE_URL = "sqlite:///./test.db"
SECRET_KEY = "secret"
ALGORITHM = "HS256"

#DB
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

#setupp
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String, default="user")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

Base.metadata.create_all(bind=engine)

#autho
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_token(data):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

#dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

 

def get_current_user(token=Depends(security)):
    try:
        payload = decode_token(token.credentials)
        return payload["user_id"]
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

#app
app = FastAPI()

@app.get("/")
def home():
    return {"message": "API running"}

#auth routes
@app.post("/api/v1/auth/register")
def register(data: dict, db: Session = Depends(get_db)):
    try:
        user = User(
            email=data["email"],
            password=hash_password(data["password"])
        )
        db.add(user)
        db.commit()
        return {"message": "User registered"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/v1/auth/login")
def login(data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data["email"]).first()

    if not user or not verify_password(data["password"], user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"user_id": user.id})
    return {"access_token": token}

#task
@app.post("/api/v1/tasks")
def create_task(data: dict, user_id=Depends(get_current_user), db: Session = Depends(get_db)):
    task = Task(
        title=data["title"],
        description=data["description"],
        user_id=user_id
    )
    db.add(task)
    db.commit()
    return {"message": "Task created"}

@app.get("/api/v1/tasks")
def get_tasks(user_id=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.user_id == user_id).all()

@app.put("/api/v1/tasks/{task_id}")
def update_task(task_id: int, data: dict, user_id=Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.title = data["title"]
    task.description = data["description"]
    db.commit()
    return {"message": "Updated"}

@app.delete("/api/v1/tasks/{task_id}")
def delete_task(task_id: int, user_id=Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Deleted"}