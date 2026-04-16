from fastapi import FastAPI
from app.database import Base, engine

# ✅ ADD THIS LINE (IMPORTANT)
from app.models import user, task  

from app.routes import auth_routes, task_routes

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(task_routes.router, prefix="/api/v1/tasks", tags=["Tasks"])

@app.get("/")
def home():
    return {"message": "API running"}