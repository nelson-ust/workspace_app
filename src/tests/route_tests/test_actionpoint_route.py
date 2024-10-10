# test_actionpoint_route.py

from typing import AsyncGenerator, Generator
import pytest
from httpx import AsyncClient
from fastapi import FastAPI, status
from sqlalchemy.orm import Session
from unittest.mock import create_autospec

from app.models.all_models import User
from app.auth.dependencies import get_db, get_current_user  # Adjust the import according to your project structure
from app.main import app  # Import your FastAPI app or initialize it here

# Set up the FastAPI app
app = FastAPI()

# Mock database session using SQLAlchemy's Session as a spec
@pytest.fixture
def test_db_session() -> Generator[Session, None, None]:
    session = create_autospec(Session, spec_set=True, instance=True)
    yield session
    session.close.assert_called()

# Mock current user
@pytest.fixture
def normal_user() -> User:
    return User(id=1, username='testuser', role='unit_member')

# Override dependency for database session and current user authentication
@pytest.fixture(autouse=True)
def override_dependency(monkeypatch, test_db_session, normal_user):
    monkeypatch.setattr(get_db, "depend", lambda: test_db_session)
    monkeypatch.setattr(get_current_user, "depend", lambda: normal_user)

# Async HTTP client using httpx
@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Test cases for action point routes
@pytest.mark.asyncio
async def test_create_actionpointsource_success(client: AsyncClient, test_db_session: Session):
    data = {"name": "New Action Point Source", "description": "Details of action point source"}
    response = await client.post("/actionpointsource/", json=data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "New Action Point Source"

@pytest.mark.asyncio
async def test_read_all_actionpointsource(client: AsyncClient, test_db_session: Session):
    response = await client.get("/actionpointsource/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_update_actionpointsource_success(client: AsyncClient, test_db_session: Session):
    actionpointsource_id = 1
    data = {"name": "Updated Action Point", "description": "Updated details"}
    response = await client.put(f"/actionpointsource/{actionpointsource_id}", json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Updated Action Point"

@pytest.mark.asyncio
async def test_delete_actionpointsource_success(client: AsyncClient, test_db_session: Session):
    actionpointsource_id = 3
    response = await client.post(f"/actionpointsource/{actionpointsource_id}/soft_delete")
    assert response.status_code == status.HTTP_200_OK
    assert "successfully deactivated" in response.json()["message"]

@pytest.mark.asyncio
async def test_restore_actionpointsource_success(client: AsyncClient, test_db_session: Session):
    actionpointsource_id = 5
    response = await client.post(f"/actionpointsource/{actionpointsource_id}/restore")
    assert response.status_code == status.HTTP_200_OK
    assert "successfully restored" in response.json()["message"]

# To run these tests, use the following command:
# pytest test_actionpoint_route.py
