from typing import List
from uuid import UUID

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from .config import settings
from .database import async_session, init_db
from .schemas import Todo, TodoCreate, TodoUpdate

app = FastAPI(
    title=settings.project_name, description=settings.description, debug=settings.debug
)


@app.on_event("startup")
async def on_startup():
    await init_db()


# Dependency
async def get_db():
    async with async_session() as session:
        yield session


@app.get("/")
async def root() -> status.HTTP_200_OK:
    return status.HTTP_200_OK


@app.get("/test")
async def test() -> str:
    return "This is a test route to test automatic deployment"


@app.get("/todos", response_model=List[Todo])
async def get_all(db: AsyncSession = Depends(get_db)) -> List[Todo]:
    return await crud.get_todos(db)


@app.get("/todos/{todo_id}", response_model=Todo)
async def get(todo_id: UUID, db: AsyncSession = Depends(get_db)) -> Todo:
    todo = await crud.get_todo(db, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    return todo


@app.post("/todos", response_model=Todo)
async def add(todo: TodoCreate, db: AsyncSession = Depends(get_db)) -> Todo:
    return await crud.create_todo(db, todo)


@app.patch("/todos/{todo_id}", response_model=Todo)
async def update(
    todo_id: UUID, todo: TodoUpdate, db: AsyncSession = Depends(get_db)
) -> Todo:
    return await crud.update_todo(db, todo_id, todo)


@app.delete("/todos/{todo_id}")
async def delete(todo_id: UUID, db: AsyncSession = Depends(get_db)) -> int:
    await crud.delete_todo(db, todo_id)
    return status.HTTP_200_OK


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
