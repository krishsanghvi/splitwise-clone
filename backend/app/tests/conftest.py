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
from app.schemas.group_members import GroupMembers
from app.schemas.categories import Categories
from app.schemas.balances import Balances
from app.schemas.expenses import Expenses
from app.schemas.expense_shares import ExpenseShares
from app.schemas.settlements import Settlements
from datetime import datetime, date
from decimal import Decimal
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


@pytest.fixture
def sample_group_member_data():
    """Sample group member data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "group_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "role": "member",
        "joined_at": datetime.now(),
        "is_active": True
    }


@pytest.fixture
def sample_group_member(sample_group_member_data):
    """Sample GroupMembers object"""
    return GroupMembers(**sample_group_member_data)


@pytest.fixture
def admin_group_member_data():
    """Sample admin group member data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "group_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "role": "admin",
        "joined_at": datetime.now(),
        "is_active": True
    }


@pytest.fixture
def multiple_group_members():
    """Multiple group members for list testing"""
    group_id = str(uuid.uuid4())
    return [
        {
            "id": str(uuid.uuid4()),
            "group_id": group_id,
            "user_id": str(uuid.uuid4()),
            "role": "member" if i > 1 else "admin",
            "joined_at": datetime.now(),
            "is_active": True
        }
        for i in range(1, 5)
    ]


@pytest.fixture
def sample_category_data():
    """Sample category data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "name": "Food & Dining",
        "icon": "utensils",
        "color": "#FF5733",
        "is_default": True,
        "created_at": datetime.now()
    }


@pytest.fixture
def sample_category(sample_category_data):
    """Sample Categories object"""
    return Categories(**sample_category_data)


@pytest.fixture
def custom_category_data():
    """Sample custom category data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "name": "Custom Category",
        "icon": "star",
        "color": "#33FF57",
        "is_default": False,
        "created_at": datetime.now()
    }


@pytest.fixture
def multiple_categories():
    """Multiple categories for list testing"""
    return [
        {
            "id": str(uuid.uuid4()),
            "name": f"Category {i}",
            "icon": f"icon{i}",
            "color": f"#FF{i}733",
            "is_default": i <= 2,
            "created_at": datetime.now()
        }
        for i in range(1, 5)
    ]


@pytest.fixture
def sample_balance_data():
    """Sample balance data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "group_id": str(uuid.uuid4()),
        "user_from": str(uuid.uuid4()),
        "user_to": str(uuid.uuid4()),
        "amount": Decimal("25.50"),
        "last_updated": datetime.now()
    }


@pytest.fixture
def sample_balance(sample_balance_data):
    """Sample Balances object"""
    return Balances(**sample_balance_data)


@pytest.fixture
def multiple_balances():
    """Multiple balances for list testing"""
    group_id = str(uuid.uuid4())
    user1 = str(uuid.uuid4())
    user2 = str(uuid.uuid4())
    user3 = str(uuid.uuid4())
    
    return [
        {
            "id": str(uuid.uuid4()),
            "group_id": group_id,
            "user_from": user1,
            "user_to": user2,
            "amount": Decimal("20.00"),
            "last_updated": datetime.now()
        },
        {
            "id": str(uuid.uuid4()),
            "group_id": group_id,
            "user_from": user2,
            "user_to": user3,
            "amount": Decimal("15.75"),
            "last_updated": datetime.now()
        },
        {
            "id": str(uuid.uuid4()),
            "group_id": group_id,
            "user_from": user3,
            "user_to": user1,
            "amount": Decimal("10.25"),
            "last_updated": datetime.now()
        }
    ]


@pytest.fixture
def balance_fixture_users():
    """Fixed user IDs for balance testing"""
    return {
        "user1": str(uuid.uuid4()),
        "user2": str(uuid.uuid4()),
        "user3": str(uuid.uuid4()),
        "group_id": str(uuid.uuid4())
    }


@pytest.fixture
def sample_expense_data():
    """Sample expense data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "group_id": str(uuid.uuid4()),
        "paid_by": str(uuid.uuid4()),
        "category_id": str(uuid.uuid4()),
        "amount": Decimal("25.50"),
        "description": "Dinner at restaurant",
        "notes": "Split equally among group members",
        "split_method": "equal",
        "expense_date": date.today().isoformat(),
        "is_reimbursement": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def sample_expense(sample_expense_data):
    """Sample Expenses object"""
    return Expenses(**sample_expense_data)


@pytest.fixture
def multiple_expenses():
    """Multiple expenses for list testing"""
    group_id = str(uuid.uuid4())
    user1 = str(uuid.uuid4())
    user2 = str(uuid.uuid4())
    category_id = str(uuid.uuid4())
    
    return [
        {
            "id": str(uuid.uuid4()),
            "group_id": group_id,
            "paid_by": user1,
            "category_id": category_id,
            "amount": Decimal("30.00"),
            "description": f"Expense {i}",
            "notes": f"Notes for expense {i}",
            "split_method": "equal",
            "expense_date": date.today().isoformat(),
            "is_reimbursement": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        for i in range(1, 4)
    ]


@pytest.fixture
def sample_expense_share_data():
    """Sample expense share data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "expense_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "amount_owned": Decimal("12.75"),
        "is_settled": False,
        "created_at": datetime.now()
    }


@pytest.fixture
def sample_expense_share(sample_expense_share_data):
    """Sample ExpenseShares object"""
    return ExpenseShares(**sample_expense_share_data)


@pytest.fixture
def multiple_expense_shares():
    """Multiple expense shares for list testing"""
    expense_id = str(uuid.uuid4())
    
    return [
        {
            "id": str(uuid.uuid4()),
            "expense_id": expense_id,
            "user_id": str(uuid.uuid4()),
            "amount_owned": Decimal(f"{10 + i}.{25 * i}"),
            "is_settled": i % 2 == 0,
            "created_at": datetime.now()
        }
        for i in range(1, 5)
    ]


@pytest.fixture
def sample_settlement_data():
    """Sample settlement data for testing"""
    return {
        "id": str(uuid.uuid4()),
        "group_id": str(uuid.uuid4()),
        "from_user": str(uuid.uuid4()),
        "to_user": str(uuid.uuid4()),
        "amount": Decimal("50.00"),
        "method": "cash",
        "reference_id": "REF123456",
        "notes": "Payment for shared expenses",
        "settled_at": datetime.now(),
        "created_at": datetime.now()
    }


@pytest.fixture
def sample_settlement(sample_settlement_data):
    """Sample Settlements object"""
    return Settlements(**sample_settlement_data)


@pytest.fixture
def multiple_settlements():
    """Multiple settlements for list testing"""
    group_id = str(uuid.uuid4())
    user1 = str(uuid.uuid4())
    user2 = str(uuid.uuid4())
    user3 = str(uuid.uuid4())
    
    return [
        {
            "id": str(uuid.uuid4()),
            "group_id": group_id,
            "from_user": user1 if i % 2 == 0 else user2,
            "to_user": user2 if i % 2 == 0 else user3,
            "amount": Decimal(f"{20 + i * 5}.00"),
            "method": "cash" if i % 2 == 0 else "digital",
            "reference_id": f"REF{i}23456",
            "notes": f"Settlement {i}",
            "settled_at": datetime.now() if i % 3 == 0 else None,
            "created_at": datetime.now()
        }
        for i in range(1, 4)
    ]
