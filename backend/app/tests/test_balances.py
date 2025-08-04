import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock
import uuid
from datetime import datetime
from decimal import Decimal


# =====================================================
# Balance CRUD Tests
# =====================================================


class TestBalanceCrud:
    """Test BalanceCRUD class directly using MagicMock"""

    @pytest.mark.asyncio
    async def test_create_balance_success(self, mock_supabase, sample_balance_data):
        """Test successful balance creation"""
        from app.crud.balances import BalanceCRUD

        # Setup: Mock get_balance_between_users returns None (no existing balance)
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        # Mock create balance
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            sample_balance_data]

        # Test
        crud = BalanceCRUD(mock_supabase)
        result = await crud.create_or_update_balance(
            group_id=sample_balance_data["group_id"],
            user_from=sample_balance_data["user_from"],
            user_to=sample_balance_data["user_to"],
            amount=Decimal("25.50")
        )

        # Assertions
        assert result is not None
        assert result.amount == Decimal("25.50")
        assert str(result.group_id) == sample_balance_data["group_id"]
        assert str(result.user_from) == sample_balance_data["user_from"]
        assert str(result.user_to) == sample_balance_data["user_to"]

        # Verify the mock chain was called correctly
        mock_supabase.table.assert_called_with('balances')

    @pytest.mark.asyncio
    async def test_update_existing_balance_success(self, mock_supabase, sample_balance_data):
        """Test updating an existing balance"""
        from app.crud.balances import BalanceCRUD

        # Setup: Mock get_balance_between_users returns existing balance
        existing_balance_data = sample_balance_data.copy()
        existing_balance_data["amount"] = Decimal("10.00")
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            existing_balance_data]

        # Mock update balance
        updated_balance_data = sample_balance_data.copy()
        updated_balance_data["amount"] = Decimal("35.50")  # 10.00 + 25.50
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            updated_balance_data]

        # Test
        crud = BalanceCRUD(mock_supabase)
        result = await crud.create_or_update_balance(
            group_id=sample_balance_data["group_id"],
            user_from=sample_balance_data["user_from"],
            user_to=sample_balance_data["user_to"],
            amount=Decimal("25.50")
        )

        # Assertions
        assert result is not None
        assert result.amount == Decimal("35.50")

    @pytest.mark.asyncio
    async def test_get_balance_by_id_success(self, mock_supabase, sample_balance_data):
        """Test successful balance retrieval by ID"""
        from app.crud.balances import BalanceCRUD

        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_balance_data]

        # Test
        crud = BalanceCRUD(mock_supabase)
        result = await crud.get_balance_by_id(sample_balance_data["id"])

        # Assertions
        assert result is not None
        assert str(result.id) == sample_balance_data["id"]
        assert result.amount == sample_balance_data["amount"]

        # Verify calls
        mock_supabase.table.assert_called_with('balances')
        mock_supabase.table.return_value.select.assert_called_with('*')

    @pytest.mark.asyncio
    async def test_get_balance_by_id_not_found(self, mock_supabase):
        """Test balance retrieval when balance doesn't exist"""
        from app.crud.balances import BalanceCRUD

        # Setup: Mock returns empty data
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Test
        crud = BalanceCRUD(mock_supabase)
        result = await crud.get_balance_by_id("nonexistent-id")

        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_get_balance_between_users_success(self, mock_supabase, sample_balance_data):
        """Test successful balance retrieval between users"""
        from app.crud.balances import BalanceCRUD

        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_balance_data]

        # Test
        crud = BalanceCRUD(mock_supabase)
        result = await crud.get_balance_between_users(
            sample_balance_data["group_id"],
            sample_balance_data["user_from"],
            sample_balance_data["user_to"]
        )

        # Assertions
        assert result is not None
        assert str(result.group_id) == sample_balance_data["group_id"]
        assert str(result.user_from) == sample_balance_data["user_from"]
        assert str(result.user_to) == sample_balance_data["user_to"]

    @pytest.mark.asyncio
    async def test_get_group_balances_success(self, mock_supabase, multiple_balances):
        """Test successful retrieval of group balances"""
        from app.crud.balances import BalanceCRUD

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_balances

        # Test
        crud = BalanceCRUD(mock_supabase)
        result = await crud.get_group_balances(multiple_balances[0]["group_id"])

        # Assertions
        assert len(result) == len(multiple_balances)
        assert all(hasattr(balance, 'amount') for balance in result)
        assert all(str(balance.group_id) == multiple_balances[0]["group_id"] for balance in result)

        # Verify calls
        mock_supabase.table.assert_called_with('balances')
        mock_supabase.table.return_value.select.assert_called_with('*')

    @pytest.mark.asyncio
    async def test_get_user_balances_in_group_success(self, mock_supabase, multiple_balances):
        """Test successful retrieval of user balances in group"""
        from app.crud.balances import BalanceCRUD

        user_id = multiple_balances[0]["user_from"]
        
        # Setup: Mock both owes and owed queries
        owes_balances = [b for b in multiple_balances if b["user_from"] == user_id]
        owed_balances = [b for b in multiple_balances if b["user_to"] == user_id]
        
        # Mock first call (owes)
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = owes_balances
        
        # Reset and mock second call (owed)
        mock_supabase.reset_mock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.side_effect = [
            type('MockResult', (), {'data': owes_balances})(),
            type('MockResult', (), {'data': owed_balances})()
        ]

        # Test
        crud = BalanceCRUD(mock_supabase)
        result = await crud.get_user_balances_in_group(multiple_balances[0]["group_id"], user_id)

        # Assertions
        assert len(result) >= 1  # At least the owes balance
        assert all(str(b.user_from) == user_id or str(b.user_to) == user_id for b in result)

    @pytest.mark.asyncio
    async def test_get_user_total_balance(self, mock_supabase, balance_fixture_users):
        """Test user total balance calculation"""
        from app.crud.balances import BalanceCRUD

        # Create test balances: user1 owes user2 $20, user3 owes user1 $10
        # Net for user1: -20 + 10 = -10 (owes $10)
        balances_data = [
            {
                "id": str(uuid.uuid4()),
                "group_id": balance_fixture_users["group_id"],
                "user_from": balance_fixture_users["user1"],
                "user_to": balance_fixture_users["user2"],
                "amount": Decimal("20.00"),
                "last_updated": datetime.now()
            },
            {
                "id": str(uuid.uuid4()),
                "group_id": balance_fixture_users["group_id"],
                "user_from": balance_fixture_users["user3"],
                "user_to": balance_fixture_users["user1"],
                "amount": Decimal("10.00"),
                "last_updated": datetime.now()
            }
        ]

        # Mock the get_user_balances_in_group method
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.side_effect = [
            type('MockResult', (), {'data': [balances_data[0]]})(),  # owes query
            type('MockResult', (), {'data': [balances_data[1]]})()   # owed query
        ]

        # Test
        crud = BalanceCRUD(mock_supabase)
        result = await crud.get_user_total_balance(
            balance_fixture_users["group_id"], 
            balance_fixture_users["user1"]
        )

        # Assertions
        assert result == Decimal("-10.00")  # User1 owes $10 net

    @pytest.mark.asyncio
    async def test_update_balance_amount_success(self, mock_supabase, sample_balance_data):
        """Test successful balance amount update"""
        from app.crud.balances import BalanceCRUD

        # Setup: Mock the update chain
        updated_data = sample_balance_data.copy()
        updated_data["amount"] = Decimal("50.00")
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            updated_data]

        # Test
        crud = BalanceCRUD(mock_supabase)
        result = await crud.update_balance_amount(
            balance_id=sample_balance_data["id"],
            new_amount=Decimal("50.00")
        )

        # Assertions
        assert result is not None
        assert result.amount == Decimal("50.00")

        # Verify calls
        mock_supabase.table.assert_called_with('balances')
        mock_supabase.table.return_value.update.assert_called_with({'amount': '50.00'})

    @pytest.mark.asyncio
    async def test_settle_balance_success(self, mock_supabase):
        """Test successful balance settlement"""
        from app.crud.balances import BalanceCRUD

        # Setup: Mock the delete chain
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [
            {"id": "test-id"}]

        # Test
        crud = BalanceCRUD(mock_supabase)
        result = await crud.settle_balance("test-id")

        # Assertions
        assert result is True

        # Verify calls
        mock_supabase.table.assert_called_with('balances')
        mock_supabase.table.return_value.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_group_balance_summary(self, mock_supabase, multiple_balances):
        """Test group balance summary calculation"""
        from app.crud.balances import BalanceCRUD

        # Setup: Mock get_group_balances
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_balances

        # Test
        crud = BalanceCRUD(mock_supabase)
        result = await crud.get_group_balance_summary(multiple_balances[0]["group_id"])

        # Assertions
        assert "group_id" in result
        assert "total_balances" in result
        assert "user_net_balances" in result
        assert "raw_balances" in result
        assert result["total_balances"] == len(multiple_balances)

    @pytest.mark.asyncio
    async def test_get_all_user_balances_success(self, mock_supabase, multiple_balances):
        """Test successful retrieval of all user balances"""
        from app.crud.balances import BalanceCRUD

        user_id = multiple_balances[0]["user_from"]
        
        # Setup: Mock both owes and owed queries across all groups
        owes_balances = [b for b in multiple_balances if b["user_from"] == user_id]
        owed_balances = [b for b in multiple_balances if b["user_to"] == user_id]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.side_effect = [
            type('MockResult', (), {'data': owes_balances})(),
            type('MockResult', (), {'data': owed_balances})()
        ]

        # Test
        crud = BalanceCRUD(mock_supabase)
        result = await crud.get_all_user_balances(user_id)

        # Assertions
        assert len(result) >= 1
        assert all(str(b.user_from) == user_id or str(b.user_to) == user_id for b in result)


# =====================================================
# Balance API Tests
# =====================================================


class TestBalanceAPI:
    """Test Balance API endpoints using MagicMock"""

    @pytest.mark.asyncio
    async def test_create_balance_success(self, async_client: AsyncClient, mock_supabase, sample_balance_data):
        """Test successful balance creation via API"""
        # Setup: Mock get_balance_between_users (no existing balance) and create_balance (success)
        # First call: get_balance_between_users returns empty (no existing balance)
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        # Second call: create_balance returns the created balance
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            sample_balance_data]

        # Test
        response = await async_client.post(
            "/api/v1/balances/",
            params={
                "group_id": sample_balance_data["group_id"],
                "user_from": sample_balance_data["user_from"],
                "user_to": sample_balance_data["user_to"],
                "amount": "25.50"
            }
        )

        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == "25.50"
        assert data["group_id"] == sample_balance_data["group_id"]
        assert data["user_from"] == sample_balance_data["user_from"]
        assert data["user_to"] == sample_balance_data["user_to"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_balance_invalid_amount(self, async_client: AsyncClient, mock_supabase, sample_balance_data):
        """Test balance creation with invalid negative amount"""
        # Test
        response = await async_client.post(
            "/api/v1/balances/",
            params={
                "group_id": sample_balance_data["group_id"],
                "user_from": sample_balance_data["user_from"],
                "user_to": sample_balance_data["user_to"],
                "amount": "-10.00"
            }
        )

        # Assertions
        assert response.status_code == 400
        assert "must be positive" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_balance_self_debt(self, async_client: AsyncClient, mock_supabase, sample_balance_data):
        """Test balance creation where user owes themselves"""
        # Test
        response = await async_client.post(
            "/api/v1/balances/",
            params={
                "group_id": sample_balance_data["group_id"],
                "user_from": sample_balance_data["user_from"],
                "user_to": sample_balance_data["user_from"],  # Same user
                "amount": "10.00"
            }
        )

        # Assertions
        assert response.status_code == 400
        assert "cannot owe money to themselves" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_balance_success(self, async_client: AsyncClient, mock_supabase, sample_balance_data):
        """Test successful balance retrieval via API"""
        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_balance_data]

        # Test
        balance_id = sample_balance_data["id"]
        response = await async_client.get(f"/api/v1/balances/{balance_id}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == balance_id
        assert data["amount"] == "25.50"

    @pytest.mark.asyncio
    async def test_get_balance_not_found(self, async_client: AsyncClient, mock_supabase):
        """Test balance retrieval when balance doesn't exist"""
        # Setup: Mock returns empty data
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Test
        response = await async_client.get("/api/v1/balances/nonexistent-id")

        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_group_balances(self, async_client: AsyncClient, mock_supabase, multiple_balances):
        """Test get group balances via API"""
        # Setup the complete mock chain for get_group_balances
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_balances

        # Test
        group_id = multiple_balances[0]["group_id"]
        response = await async_client.get(f"/api/v1/balances/group/{group_id}/balances")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("amount" in balance for balance in data)

    @pytest.mark.asyncio
    async def test_get_user_balances_in_group(self, async_client: AsyncClient, mock_supabase, multiple_balances):
        """Test get user balances in group via API"""
        # Setup
        user_id = multiple_balances[0]["user_from"]
        group_id = multiple_balances[0]["group_id"]
        
        owes_balances = [b for b in multiple_balances if b["user_from"] == user_id]
        owed_balances = [b for b in multiple_balances if b["user_to"] == user_id]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.side_effect = [
            type('MockResult', (), {'data': owes_balances})(),
            type('MockResult', (), {'data': owed_balances})()
        ]

        # Test
        response = await async_client.get(f"/api/v1/balances/group/{group_id}/user/{user_id}/balances")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_user_total_balance(self, async_client: AsyncClient, mock_supabase, balance_fixture_users):
        """Test get user total balance via API"""
        # Setup: Mock the balance calculation
        balances_data = [
            {
                "id": str(uuid.uuid4()),
                "group_id": balance_fixture_users["group_id"],
                "user_from": balance_fixture_users["user1"],
                "user_to": balance_fixture_users["user2"],
                "amount": Decimal("20.00"),
                "last_updated": datetime.now()
            }
        ]

        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.side_effect = [
            type('MockResult', (), {'data': balances_data})(),  # owes query
            type('MockResult', (), {'data': []})()              # owed query
        ]

        # Test
        response = await async_client.get(
            f"/api/v1/balances/group/{balance_fixture_users['group_id']}/user/{balance_fixture_users['user1']}/total"
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "net_balance" in data
        assert "status" in data
        assert data["status"] == "owes_money"

    @pytest.mark.asyncio
    async def test_get_group_balance_summary(self, async_client: AsyncClient, mock_supabase, multiple_balances):
        """Test get group balance summary via API"""
        # Setup
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_balances

        # Test
        group_id = multiple_balances[0]["group_id"]
        response = await async_client.get(f"/api/v1/balances/group/{group_id}/summary")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "group_id" in data
        assert "total_balances" in data
        assert "user_net_balances" in data

    @pytest.mark.asyncio
    async def test_get_all_user_balances(self, async_client: AsyncClient, mock_supabase, multiple_balances):
        """Test get all user balances via API"""
        # Setup
        user_id = multiple_balances[0]["user_from"]
        
        owes_balances = [b for b in multiple_balances if b["user_from"] == user_id]
        owed_balances = [b for b in multiple_balances if b["user_to"] == user_id]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.side_effect = [
            type('MockResult', (), {'data': owes_balances})(),
            type('MockResult', (), {'data': owed_balances})()
        ]

        # Test
        response = await async_client.get(f"/api/v1/balances/user/{user_id}/balances")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_balance_between_users_success(self, async_client: AsyncClient, mock_supabase, sample_balance_data):
        """Test successful balance retrieval between users via API"""
        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_balance_data]

        # Test
        response = await async_client.get(
            f"/api/v1/balances/between?group_id={sample_balance_data['group_id']}&user_from={sample_balance_data['user_from']}&user_to={sample_balance_data['user_to']}"
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["group_id"] == sample_balance_data["group_id"]
        assert data["user_from"] == sample_balance_data["user_from"]
        assert data["user_to"] == sample_balance_data["user_to"]

    @pytest.mark.asyncio
    async def test_get_balance_between_users_not_found(self, async_client: AsyncClient, mock_supabase):
        """Test balance between users when no balance exists"""
        # Setup: Mock returns empty data
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        # Test
        response = await async_client.get(
            "/api/v1/balances/between?group_id=group1&user_from=user1&user_to=user2"
        )

        # Assertions
        assert response.status_code == 404
        assert "balance found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_balance_amount_success(self, async_client: AsyncClient, mock_supabase, sample_balance_data):
        """Test successful balance amount update via API"""
        # Setup: Mock get_balance_by_id (balance exists) and update_balance_amount (success)
        # First call: get_balance_by_id returns existing balance
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_balance_data]

        # Second call: update_balance_amount returns updated balance
        updated_data = sample_balance_data.copy()
        updated_data["amount"] = Decimal("50.00")
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            updated_data]

        # Test
        response = await async_client.put(
            f"/api/v1/balances/{sample_balance_data['id']}/amount",
            params={"amount": "50.00"}
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == "50.00"

    @pytest.mark.asyncio
    async def test_update_balance_amount_invalid(self, async_client: AsyncClient, mock_supabase, sample_balance_data):
        """Test balance amount update with invalid amount"""
        # Test
        response = await async_client.put(
            f"/api/v1/balances/{sample_balance_data['id']}/amount",
            params={"amount": "-10.00"}
        )

        # Assertions
        assert response.status_code == 400
        assert "must be positive" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_balance_amount_not_found(self, async_client: AsyncClient, mock_supabase):
        """Test balance amount update when balance doesn't exist"""
        # Setup: Mock returns empty data for balance lookup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Test
        response = await async_client.put(
            "/api/v1/balances/nonexistent-id/amount",
            params={"amount": "50.00"}
        )

        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_settle_balance_success(self, async_client: AsyncClient, mock_supabase, sample_balance_data):
        """Test successful balance settlement via API"""
        # Setup: Mock get_balance_by_id (balance exists) and settle_balance (success)
        # First call: get_balance_by_id returns existing balance
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_balance_data]

        # Second call: settle_balance (delete) returns success
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [
            {"id": sample_balance_data["id"]}]

        # Test
        response = await async_client.delete(f"/api/v1/balances/{sample_balance_data['id']}/settle")

        # Assertions
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_settle_balance_not_found(self, async_client: AsyncClient, mock_supabase):
        """Test balance settlement when balance doesn't exist"""
        # Setup: Mock returns empty data for balance lookup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Test
        response = await async_client.delete("/api/v1/balances/nonexistent-id/settle")

        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


# =====================================================
# Edge Cases and Error Scenarios
# =====================================================


class TestBalanceCrudEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.mark.asyncio
    async def test_get_group_balances_database_error(self, mock_supabase):
        """Test get group balances when database throws an error"""
        from app.crud.balances import BalanceCRUD

        # Setup: Mock raises an exception
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.side_effect = Exception(
            "Database error")

        # Test
        crud = BalanceCRUD(mock_supabase)
        result = await crud.get_group_balances("group-id")

        # Assertions - should return empty list on error
        assert result == []

    @pytest.mark.asyncio
    async def test_create_balance_database_exception(self, mock_supabase):
        """Test balance creation when database throws an exception"""
        from app.crud.balances import BalanceCRUD

        # Setup: Mock get_balance_between_users returns None, then insert raises exception
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception(
            "Database error")

        # Test
        crud = BalanceCRUD(mock_supabase)
        result = await crud.create_or_update_balance(
            group_id=str(uuid.uuid4()),
            user_from=str(uuid.uuid4()),
            user_to=str(uuid.uuid4()),
            amount=Decimal("10.00")
        )

        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_total_balance_database_exception(self, mock_supabase):
        """Test user total balance calculation when database throws an exception"""
        from app.crud.balances import BalanceCRUD

        # Setup: Mock raises an exception
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.side_effect = Exception(
            "Database error")

        # Test
        crud = BalanceCRUD(mock_supabase)
        result = await crud.get_user_total_balance("group-id", "user-id")

        # Assertions
        assert result == Decimal('0')  # Should return 0 on error