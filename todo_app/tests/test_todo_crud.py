from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, models, schemas
from ..database import async_session, init_db


@pytest_asyncio.fixture()
async def initialise_db():
    await init_db()


@pytest_asyncio.fixture
async def db(initialise_db):
    async with async_session() as session:
        yield session


@pytest.mark.asyncio
async def test_create_todo(db: AsyncSession):
    create_todo = schemas.TodoCreate(title="Test Todo Item")
    todo = await crud.create_todo(db, create_todo)

    db_todo = await db.get(models.Todo, str(todo.id))

    assert db_todo is not None
    assert db_todo.id == str(todo.id)
    assert db_todo.title == todo.title
    assert db_todo.completed == todo.completed


@pytest.mark.asyncio
async def test_delete_todo(db: AsyncSession):
    db_todo = models.Todo(title="Test Todo Item")
    db.add(db_todo)
    await db.commit()
    await db.refresh(db_todo)

    await crud.delete_todo(db, UUID(db_todo.id))

    result = await db.execute(
        select(models.Todo).where(models.Todo.id == str(db_todo.id))
    )
    assert len(result.scalars().all()) == 0


@pytest.mark.asyncio
async def test_update_todo(db: AsyncSession):
    db_todo = models.Todo(title="Test Todo Item")
    db.add(db_todo)
    await db.commit()
    await db.refresh(db_todo)

    todo_update = schemas.TodoUpdate(title="Updated Test Todo Item", completed=True)
    todo_update = await crud.update_todo(db, UUID(db_todo.id), todo_update)

    assert todo_update.id == db_todo.id
    assert todo_update.title == db_todo.title
    assert todo_update.completed == db_todo.completed
    assert todo_update.created_at == db_todo.created_at


@pytest.mark.asyncio
async def test_get_todos(db: AsyncSession):
    db_todos = [models.Todo(title="Test Todo #1"), models.Todo(title="Test Todo #2")]

    for todo in db_todos:
        db.add(todo)
        await db.commit()
        await db.refresh(todo)

    fetched_todos = await crud.get_todos(db)

    for db_todo in db_todos:
        assert db_todo in fetched_todos


@pytest.mark.asyncio
async def test_get_todo(db: AsyncSession):
    db_todo = models.Todo(title="Test Todo Item")
    db.add(db_todo)
    await db.commit()
    await db.refresh(db_todo)

    todo = await crud.get_todo(db, UUID(db_todo.id))

    assert todo.id == db_todo.id
    assert todo.title == db_todo.title
    assert todo.completed == db_todo.completed
    assert todo.created_at == db_todo.created_at
