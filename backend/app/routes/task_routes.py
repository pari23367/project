from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task_schema import TaskCreate
from app.auth.dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/")
def create_task(task: TaskCreate, user_id=Depends(get_current_user), db: Session = Depends(get_db)):
    new_task = Task(
        title=task.title,
        description=task.description,
        user_id=user_id
    )
    db.add(new_task)
    db.commit()
    return {"message": "Task created"}

@router.get("/")
def get_tasks(user_id=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.user_id == user_id).all()

@router.put("/{task_id}")
def update_task(task_id: int, task: TaskCreate, user_id=Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    db_task.title = task.title
    db_task.description = task.description
    db.commit()

    return {"message": "Updated"}

@router.delete("/{task_id}")
def delete_task(task_id: int, user_id=Depends(get_current_user), db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(db_task)
    db.commit()

    return {"message": "Deleted"}