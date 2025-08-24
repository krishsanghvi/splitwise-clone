import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import uuid
from datetime import datetime
from decimal import Decimal


class TestSettlementsCrud:
    """Test SettlementsCRUD class directly using MagicMock"""

    @pytest.mark.asyncio
    async def test_create_settlement_success(self, mock_supabase, sample_settlement_data):
        """Test successful settlement creation"""
        from app.crud.settlements import SettlementsCRUD

        # Setup: Mock the entire chain and set the final result
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            sample_settlement_data]

        # Test
        crud = SettlementsCRUD(mock_supabase)
        result = await crud.create_settlement(
            group_id=sample_settlement_data["group_id"],
            from_user=sample_settlement_data["from_user"],
            to_user=sample_settlement_data["to_user"],
            amount=str(sample_settlement_data["amount"]),
            method=sample_settlement_data["method"]
        )

        # Assertions
        assert result is not None
        assert str(result.group_id) == sample_settlement_data["group_id"]
        assert str(result.from_user) == sample_settlement_data["from_user"]
        assert str(result.to_user) == sample_settlement_data["to_user"]
        assert result.method == sample_settlement_data["method"]

        # Verify the mock chain was called correctly
        mock_supabase.table.assert_called_with('settlements')
        mock_supabase.table.return_value.insert.assert_called_once()
        mock_supabase.table.return_value.insert.return_value.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_settlement_success(self, mock_supabase, sample_settlement_data):
        """Test successful settlement retrieval by ID"""
        from app.crud.settlements import SettlementsCRUD

        # Setup: Mock the select().eq().execute() chain
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_settlement_data]

        # Test
        crud = SettlementsCRUD(mock_supabase)
        result = await crud.get_settlement_by_id(sample_settlement_data["id"])

        # Assertions
        assert result is not None
        assert str(result.id) == sample_settlement_data["id"]
        assert str(result.group_id) == sample_settlement_data["group_id"]
        assert result.method == sample_settlement_data["method"]

        # Verify calls
        mock_supabase.table.assert_called_with('settlements')
        mock_supabase.table.return_value.select.assert_called_with('*')
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with(
            'id', sample_settlement_data["id"])

    @pytest.mark.asyncio
    async def test_get_settlements_by_group_success(self, mock_supabase, multiple_settlements):
        """Test successful retrieval of settlements by group"""
        from app.crud.settlements import SettlementsCRUD

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_settlements

        # Test
        crud = SettlementsCRUD(mock_supabase)
        result = await crud.get_settlements_by_group(multiple_settlements[0]["group_id"])

        # Assertions
        assert len(result) == len(multiple_settlements)
        assert all(hasattr(settlement, 'amount') for settlement in result)
        assert all(hasattr(settlement, 'method') for settlement in result)

        # Verify calls
        mock_supabase.table.assert_called_with('settlements')
        mock_supabase.table.return_value.select.assert_called_with('*')
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with(
            'group_id', multiple_settlements[0]["group_id"])

    @pytest.mark.asyncio
    async def test_get_settlements_by_user_success(self, mock_supabase, multiple_settlements):
        """Test successful retrieval of settlements by user"""
        from app.crud.settlements import SettlementsCRUD

        # Filter settlements by user (either from_user or to_user)
        user_id = multiple_settlements[0]["from_user"]
        user_settlements = [settlement for settlement in multiple_settlements 
                          if settlement["from_user"] == user_id or settlement["to_user"] == user_id]

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.or_.return_value.order.return_value.range.return_value.execute.return_value.data = user_settlements

        # Test
        crud = SettlementsCRUD(mock_supabase)
        result = await crud.get_settlements_by_user(user_id)

        # Assertions
        assert len(result) == len(user_settlements)
        assert all(str(settlement.from_user) == user_id or str(settlement.to_user) == user_id 
                  for settlement in result)

        # Verify calls
        mock_supabase.table.assert_called_with('settlements')

    @pytest.mark.asyncio
    async def test_get_settlements_from_user_success(self, mock_supabase, multiple_settlements):
        """Test successful retrieval of settlements from user"""
        from app.crud.settlements import SettlementsCRUD

        # Filter settlements by from_user
        from_user = multiple_settlements[0]["from_user"]
        from_user_settlements = [settlement for settlement in multiple_settlements 
                               if settlement["from_user"] == from_user]

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = from_user_settlements

        # Test
        crud = SettlementsCRUD(mock_supabase)
        result = await crud.get_settlements_from_user(from_user)

        # Assertions
        assert len(result) == len(from_user_settlements)
        assert all(str(settlement.from_user) == from_user for settlement in result)

        # Verify calls
        mock_supabase.table.assert_called_with('settlements')
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with(
            'from_user', from_user)

    @pytest.mark.asyncio
    async def test_get_pending_settlements_success(self, mock_supabase, multiple_settlements):
        """Test successful retrieval of pending settlements"""
        from app.crud.settlements import SettlementsCRUD

        # Filter pending settlements (settled_at is None)
        pending_settlements = [settlement for settlement in multiple_settlements 
                             if settlement["settled_at"] is None]

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.is_.return_value.order.return_value.range.return_value.execute.return_value.data = pending_settlements

        # Test
        crud = SettlementsCRUD(mock_supabase)
        result = await crud.get_pending_settlements()

        # Assertions
        assert len(result) == len(pending_settlements)
        assert all(settlement.settled_at is None for settlement in result)

        # Verify calls
        mock_supabase.table.assert_called_with('settlements')
        mock_supabase.table.return_value.select.return_value.is_.assert_called_with(
            'settled_at', 'null')

    @pytest.mark.asyncio
    async def test_mark_settlement_completed_success(self, mock_supabase, sample_settlement_data):
        """Test successful settlement completion"""
        from app.crud.settlements import SettlementsCRUD

        # Setup: Mock update chain
        completed_data = sample_settlement_data.copy()
        completed_data["settled_at"] = datetime.now()
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            completed_data]

        # Test
        crud = SettlementsCRUD(mock_supabase)
        result = await crud.mark_settlement_completed(sample_settlement_data["id"])

        # Assertions
        assert result is not None
        assert result.settled_at is not None

        # Verify calls
        mock_supabase.table.assert_called_with('settlements')
        mock_supabase.table.return_value.update.assert_called_once()
        mock_supabase.table.return_value.update.return_value.eq.assert_called_with(
            'id', sample_settlement_data["id"])

    @pytest.mark.asyncio
    async def test_mark_settlement_pending_success(self, mock_supabase, sample_settlement_data):
        """Test successful settlement pending marking"""
        from app.crud.settlements import SettlementsCRUD

        # Setup: Mock update chain
        pending_data = sample_settlement_data.copy()
        pending_data["settled_at"] = None
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            pending_data]

        # Test
        crud = SettlementsCRUD(mock_supabase)
        result = await crud.mark_settlement_pending(sample_settlement_data["id"])

        # Assertions
        assert result is not None
        assert result.settled_at is None

        # Verify calls
        mock_supabase.table.assert_called_with('settlements')
        mock_supabase.table.return_value.update.return_value.eq.assert_called_with(
            'id', sample_settlement_data["id"])

    @pytest.mark.asyncio
    async def test_update_settlement_success(self, mock_supabase, sample_settlement_data):
        """Test successful settlement update"""
        from app.crud.settlements import SettlementsCRUD

        # Setup: Mock update chain
        updated_data = sample_settlement_data.copy()
        updated_data["method"] = "digital"
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            updated_data]

        # Test
        crud = SettlementsCRUD(mock_supabase)
        result = await crud.update_settlement(
            sample_settlement_data["id"], 
            method="digital"
        )

        # Assertions
        assert result is not None
        assert result.method == "digital"

        # Verify calls
        mock_supabase.table.assert_called_with('settlements')
        mock_supabase.table.return_value.update.assert_called_once()
        mock_supabase.table.return_value.update.return_value.eq.assert_called_with(
            'id', sample_settlement_data["id"])

    @pytest.mark.asyncio
    async def test_delete_settlement_success(self, mock_supabase, sample_settlement_data):
        """Test successful settlement deletion"""
        from app.crud.settlements import SettlementsCRUD

        # Setup: Mock delete chain
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [
            sample_settlement_data]

        # Test
        crud = SettlementsCRUD(mock_supabase)
        result = await crud.delete_settlement(sample_settlement_data["id"])

        # Assertions
        assert result is True

        # Verify calls
        mock_supabase.table.assert_called_with('settlements')
        mock_supabase.table.return_value.delete.return_value.eq.assert_called_with(
            'id', sample_settlement_data["id"])

    @pytest.mark.asyncio
    async def test_get_settlements_between_users_success(self, mock_supabase, multiple_settlements):
        """Test successful retrieval of settlements between two users"""
        from app.crud.settlements import SettlementsCRUD

        # Get two users from the settlements
        user1_id = multiple_settlements[0]["from_user"]
        user2_id = multiple_settlements[0]["to_user"]
        
        # Filter settlements between these users
        between_settlements = [settlement for settlement in multiple_settlements 
                             if (settlement["from_user"] == user1_id and settlement["to_user"] == user2_id) or
                                (settlement["from_user"] == user2_id and settlement["to_user"] == user1_id)]

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.or_.return_value.order.return_value.execute.return_value.data = between_settlements

        # Test
        crud = SettlementsCRUD(mock_supabase)
        result = await crud.get_settlements_between_users(user1_id, user2_id)

        # Assertions
        assert len(result) == len(between_settlements)

        # Verify calls
        mock_supabase.table.assert_called_with('settlements')


class TestSettlementsAPI:
    """Test Settlements API endpoints using MagicMock"""

    @pytest.mark.asyncio
    async def test_create_settlement_success(self, async_client: AsyncClient, mock_supabase, sample_settlement_data):
        """Test successful settlement creation via API"""
        # Setup: Mock create_settlement success
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            sample_settlement_data]

        # Test
        response = await async_client.post(
            "/api/v1/settlements/",
            params={
                "group_id": sample_settlement_data["group_id"],
                "from_user": sample_settlement_data["from_user"],
                "to_user": sample_settlement_data["to_user"],
                "amount": str(sample_settlement_data["amount"]),
                "method": sample_settlement_data["method"]
            }
        )

        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["group_id"] == sample_settlement_data["group_id"]
        assert data["from_user"] == sample_settlement_data["from_user"]
        assert data["method"] == sample_settlement_data["method"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_settlement_same_users_error(self, async_client: AsyncClient, mock_supabase, sample_settlement_data):
        """Test settlement creation error when from_user and to_user are the same"""
        # Test
        response = await async_client.post(
            "/api/v1/settlements/",
            params={
                "group_id": sample_settlement_data["group_id"],
                "from_user": sample_settlement_data["from_user"],
                "to_user": sample_settlement_data["from_user"],  # Same as from_user
                "amount": str(sample_settlement_data["amount"]),
                "method": sample_settlement_data["method"]
            }
        )

        # Assertions
        assert response.status_code == 400
        assert "cannot be the same" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_settlement_success(self, async_client: AsyncClient, mock_supabase, sample_settlement_data):
        """Test successful settlement retrieval via API"""
        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_settlement_data]

        # Test
        settlement_id = sample_settlement_data["id"]
        response = await async_client.get(f"/api/v1/settlements/{settlement_id}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == settlement_id
        assert data["method"] == sample_settlement_data["method"]

    @pytest.mark.asyncio
    async def test_get_settlements_by_group(self, async_client: AsyncClient, mock_supabase, multiple_settlements):
        """Test get settlements by group via API"""
        # Setup the complete mock chain for get_settlements_by_group
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_settlements

        # Test
        group_id = multiple_settlements[0]["group_id"]
        response = await async_client.get(f"/api/v1/settlements/group/{group_id}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(multiple_settlements)
        assert all("amount" in settlement for settlement in data)

    @pytest.mark.asyncio
    async def test_get_settlements_by_user(self, async_client: AsyncClient, mock_supabase, multiple_settlements):
        """Test get settlements by user via API"""
        # Filter settlements by user
        user_id = multiple_settlements[0]["from_user"]
        user_settlements = [settlement for settlement in multiple_settlements 
                          if settlement["from_user"] == user_id or settlement["to_user"] == user_id]
        
        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.or_.return_value.order.return_value.range.return_value.execute.return_value.data = user_settlements

        # Test
        response = await async_client.get(f"/api/v1/settlements/user/{user_id}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(user_settlements)

    @pytest.mark.asyncio
    async def test_get_pending_settlements(self, async_client: AsyncClient, mock_supabase, multiple_settlements):
        """Test get pending settlements via API"""
        # Filter pending settlements
        pending_settlements = [settlement for settlement in multiple_settlements 
                             if settlement["settled_at"] is None]
        
        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.is_.return_value.order.return_value.range.return_value.execute.return_value.data = pending_settlements

        # Test
        response = await async_client.get("/api/v1/settlements/")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(pending_settlements)

    @pytest.mark.asyncio
    async def test_mark_settlement_completed(self, async_client: AsyncClient, mock_supabase, sample_settlement_data):
        """Test marking settlement as completed via API"""
        # Setup: First call to check if settlement exists
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_settlement_data]

        # Setup: Second call for completion
        completed_data = sample_settlement_data.copy()
        completed_data["settled_at"] = datetime.now().isoformat()
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            completed_data]

        # Test
        settlement_id = sample_settlement_data["id"]
        response = await async_client.put(f"/api/v1/settlements/{settlement_id}/complete")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["settled_at"] is not None

    @pytest.mark.asyncio
    async def test_get_settlement_not_found(self, async_client: AsyncClient, mock_supabase):
        """Test settlement retrieval when settlement doesn't exist"""
        # Setup: Mock returns empty data
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Test
        response = await async_client.get("/api/v1/settlements/nonexistent-id")

        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_settlement_success(self, async_client: AsyncClient, mock_supabase, sample_settlement_data):
        """Test successful settlement deletion via API"""
        # Setup: First call to check if settlement exists
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_settlement_data]

        # Setup: Second call for deletion
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [
            sample_settlement_data]

        # Test
        settlement_id = sample_settlement_data["id"]
        response = await async_client.delete(f"/api/v1/settlements/{settlement_id}")

        # Assertions
        assert response.status_code == 204


class TestSettlementsCrudEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.mark.asyncio
    async def test_get_settlements_by_group_database_error(self, mock_supabase):
        """Test get settlements by group when database throws an error"""
        from app.crud.settlements import SettlementsCRUD

        # Setup: Mock raises an exception
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.side_effect = Exception(
            "Database error")

        # Test
        crud = SettlementsCRUD(mock_supabase)
        result = await crud.get_settlements_by_group("group-id")

        # Assertions - should return empty list on error
        assert result == []

    @pytest.mark.asyncio
    async def test_create_settlement_failure(self, mock_supabase):
        """Test settlement creation failure when database returns no data"""
        from app.crud.settlements import SettlementsCRUD

        # Setup: Mock returns None/empty data
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = None

        # Test
        crud = SettlementsCRUD(mock_supabase)
        result = await crud.create_settlement(
            group_id=str(uuid.uuid4()),
            from_user=str(uuid.uuid4()),
            to_user=str(uuid.uuid4()),
            amount="50.00"
        )

        # Assertions
        assert result is None