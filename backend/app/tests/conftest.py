import pytest
import asyncio
from typing import AsyncGenerator, Iterator
from httpx import AsyncClient
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import pytest_asyncio
from app.main import app
from app.database import get_supabase
from app.schemas.users import User
from app.schemas.groups import Groups
from datetime import datetime
import uuid


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_supabase():
    """Mock Supabase client using MagicMock for easier testing"""
    # MagicMock handles method chaining automatically
    mock_client = MagicMock()

    # Reset the mock for each test to avoid state leakage
    mock_client.reset_mock(return_value=True, side_effect=True)

    return mock_client


@pytest.fixture
def override_get_supabase(mock_supabase):
    """Override the Supabase dependency"""
    def _get_supabase_override(admin: bool = False):
        return mock_supabase
    return _get_supabase_override


@pytest_asyncio.fixture
async def async_client(override_get_supabase) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client with mocked dependencies"""
    app.dependency_overrides[get_supabase] = override_get_supabase

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    # Clean up
    app.dependency_overrides.clear()


# Rest of conftest.py remains the same...
@pytest.fixture
def sync_client(override_get_supabase) -> Iterator[TestClient]:
    """Create synchronous test client (alternative to async)"""
    app.dependency_overrides[get_supabase] = override_get_supabase

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "full_name": "Test User",
        "timezone": "UTC",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def sample_user(sample_user_data):
    """Sample User object"""
    return User(**sample_user_data)


@pytest.fixture
def multiple_users():
    """Multiple users for list testing"""
    return [
        {
            "id": str(uuid.uuid4()),
            "email": f"test{i}@example.com",
            "full_name": f"Test User {i}",
            "timezone": "UTC",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        for i in range(1, 4)
    ]


@pytest.fixture
def sample_group_data():
    """Sample group data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "created_by": str(uuid.uuid4()),
        "group_name": "Test Group",
        "group_description": "Test Description",
        "invite_code": "TEST123",
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def sample_group(sample_group_data):
    """Sample Group object"""
    return Groups(**sample_group_data)


@pytest.fixture
def multiple_groups():
    """Multiple groups for list testing"""
    creator_id = str(uuid.uuid4())
    return [
        {
            "id": str(uuid.uuid4()),
            "created_by": creator_id,
            "group_name": f"Test Group {i}",
            "group_description": f"Test Description {i}",
            "invite_code": f"TEST{i}",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        for i in range(1, 4)
    ]
