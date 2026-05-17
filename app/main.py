from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db, init_db, TodoUser, TodoCategory, TodoTask

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


class TodoCreate(BaseModel):
    title: str
    category_id: int


class TodoUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None
    category_id: int | None = None


def get_current_user(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    user = db.query(TodoUser).filter(TodoUser.api_key == x_api_key).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user


@app.get("/")
def default_endpoint():
    return {
        "message": "ToDo API is running",
        "endpoints": [
            "GET /todos",
            "POST /todos",
            "PUT /todos/{id}",
            "DELETE /todos/{id}",
            "GET /categories"
        ]
    }


@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return db.query(TodoCategory).order_by(TodoCategory.id.asc()).all()


@app.get("/todos")
def get_todos(
    db: Session = Depends(get_db),
    current_user: TodoUser = Depends(get_current_user)
):
    tasks = (
        db.query(TodoTask)
        .filter(TodoTask.user_id == current_user.id)
        .order_by(TodoTask.id.desc())
        .all()
    )

    return [
        {
            "id": task.id,
            "title": task.title,
            "done": task.done,
            "category_id": task.category_id,
            "category_name": task.category.category_name if task.category else None,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        }
        for task in tasks
    ]


@app.post("/todos")
def create_todo(
    payload: TodoCreate,
    db: Session = Depends(get_db),
    current_user: TodoUser = Depends(get_current_user)
):
    category = db.query(TodoCategory).filter(TodoCategory.id == payload.category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    task = TodoTask(
        user_id=current_user.id,
        category_id=payload.category_id,
        title=payload.title,
        done=False
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "title": task.title,
        "done": task.done,
        "category_id": task.category_id,
        "category_name": task.category.category_name if task.category else None
    }


@app.put("/todos/{id}")
def update_todo(
    id: int,
    payload: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: TodoUser = Depends(get_current_user)
):
    task = (
        db.query(TodoTask)
        .filter(TodoTask.id == id, TodoTask.user_id == current_user.id)
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Todo not found")

    if payload.title is not None:
        task.title = payload.title

    if payload.done is not None:
        task.done = payload.done

    if payload.category_id is not None:
        category = db.query(TodoCategory).filter(TodoCategory.id == payload.category_id).first()

        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        task.category_id = payload.category_id

    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "title": task.title,
        "done": task.done,
        "category_id": task.category_id,
        "category_name": task.category.category_name if task.category else None
    }


@app.delete("/todos/{id}")
def delete_todo(
    id: int,
    db: Session = Depends(get_db),
    current_user: TodoUser = Depends(get_current_user)
):
    task = (
        db.query(TodoTask)
        .filter(TodoTask.id == id, TodoTask.user_id == current_user.id)
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(task)
    db.commit()

    return {"deleted": id}