from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate
from app.services.auth_deps import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/", response_model=List[TaskOut])
def list_tasks(status: Optional[str] = None, priority: Optional[str] = None, skip: int = 0, limit: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Task)
    if current_user.role != "admin":
        q = q.filter(Task.owner_id == current_user.id)
    if status: q = q.filter(Task.status == status)
    if priority: q = q.filter(Task.priority == priority)
    return q.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = Task(**payload.model_dump(), owner_id=current_user.id)
    db.add(task); db.commit(); db.refresh(task)
    return task

@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task: raise HTTPException(status_code=404, detail="Task not found")
    if current_user.role != "admin" and task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return task

@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task: raise HTTPException(status_code=404, detail="Task not found")
    if current_user.role != "admin" and task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    db.commit(); db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task: raise HTTPException(status_code=404, detail="Task not found")
    if current_user.role != "admin" and task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(task); db.commit()
