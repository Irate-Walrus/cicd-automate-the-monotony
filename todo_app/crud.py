from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas


async def get_todo(db: AsyncSession, todo_id: UUID):
    return await db.get(models.Todo, str(todo_id))


async def get_todos(db: AsyncSession):
    res = await db.execute(select(models.Todo))
    return res.scalars().all()


async def create_todo(db: AsyncSession, todo_create: schemas.TodoCreate):
    new_todo = models.Todo(title=todo_create.title, completed=todo_create.completed)
    db.add(new_todo)
    await db.commit()
    await db.refresh(new_todo)
    return new_todo


async def update_todo(db: AsyncSession, todo_id: UUID, todo_update: schemas.TodoUpdate):
    todo: models.Todo = await db.get(models.Todo, str(todo_id))

    if todo_update.title is not None:
        todo.title = todo_update.title

    if todo_update.completed is not None:
        todo.completed = todo_update.completed

    await db.commit()
    await db.refresh(todo)
    return todo


async def delete_todo(db: AsyncSession, todo_id: UUID):
    todo = await db.get(models.Todo, str(todo_id))
    if todo:
        await db.delete(todo)
        await db.commit()
