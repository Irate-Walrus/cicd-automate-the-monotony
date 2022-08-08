from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..database import async_session, init_db
from ..main import app


@pytest_asyncio.fixture()
async def initialise_db():
    await init_db()


@pytest_asyncio.fixture
async def httpx_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def db(initialise_db):
    async with async_session() as session:
        yield session


@pytest.mark.asyncio
async def test_create_todo(httpx_client: AsyncClient, db: AsyncSession):
    create_todo = schemas.TodoCreate(title="Test Todo Item")

    response = await httpx_client.post("/todos", content=create_todo.json())
    assert response.status_code == 200

    todo = schemas.Todo.validate(response.json())

    assert todo.id is not None
    assert todo.title == create_todo.title
    assert todo.completed == False

    db_todo = await db.get(models.Todo, str(todo.id))

    assert db_todo is not None
    assert db_todo.id == str(todo.id)
    assert db_todo.title == todo.title
    assert db_todo.completed == todo.completed


@pytest.mark.asyncio
async def test_delete_todo(httpx_client: AsyncClient, db: AsyncSession):
    db_todo = models.Todo(title="Test Todo Item")
    db.add(db_todo)
    await db.commit()
    await db.refresh(db_todo)

    todo = schemas.Todo.validate(db_todo)

    delete_response = await httpx_client.delete(f"/todos/{todo.id}")
    assert delete_response.status_code == 200

    result = await db.execute(select(models.Todo).where(models.Todo.id == str(todo.id)))
    assert len(result.scalars().all()) == 0


@pytest.mark.asyncio
async def test_update_todo(httpx_client: AsyncClient, db: AsyncSession):
    db_todo = models.Todo(title="Test Todo Item")
    db.add(db_todo)
    await db.commit()
    await db.refresh(db_todo)

    todo_update = schemas.TodoUpdate(title="Updated Todo Item", completed=True)

    response = await httpx_client.patch(
        f"/todos/{db_todo.id}", content=todo_update.json()
    )
    assert response.status_code == 200

    todo = schemas.Todo.validate(response.json())
    assert str(todo.id) == db_todo.id
    assert todo.title == todo_update.title
    assert todo.completed == todo_update.completed
    assert todo.created_at == db_todo.created_at


@pytest.mark.asyncio
async def test_get_todos(httpx_client: AsyncClient, db: AsyncSession):
    db_todos = [models.Todo(title="Test Todo #1"), models.Todo(title="Test Todo #2")]

    for todo in db_todos:
        db.add(todo)
        await db.commit()
        await db.refresh(todo)

    response = await httpx_client.get("/todos")
    assert response.status_code == 200

    todo_list = [schemas.Todo.validate(todo) for todo in response.json()]

    for db_todo in db_todos:
        assert schemas.Todo.from_orm(db_todo) in todo_list


@pytest.mark.asyncio
async def test_get_todo(httpx_client: AsyncClient, db: AsyncSession):
    db_todo = models.Todo(title="Test Todo Item")
    db.add(db_todo)
    await db.commit()
    await db.refresh(db_todo)

    response = await httpx_client.get(f"/todos/{db_todo.id}")
    assert response.status_code == 200

    todo = schemas.Todo.validate(response.json())
    assert str(todo.id) == db_todo.id
    assert todo.title == db_todo.title
    assert todo.completed == db_todo.completed
    assert todo.created_at == db_todo.created_at


@pytest.mark.asyncio
async def test_get_null_todo(httpx_client: AsyncClient, db: AsyncSession):
    db_todo = models.Todo(title="Test Todo Item")
    db.add(db_todo)
    await db.commit()
    await db.refresh(db_todo)

    response = await httpx_client.get(f"/todos/{uuid4()}")
    assert response.status_code == 404
