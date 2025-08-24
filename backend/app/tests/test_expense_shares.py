import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import uuid
from datetime import datetime
from decimal import Decimal


class TestExpenseSharesCrud:
    """Test ExpenseSharesCRUD class directly using MagicMock"""

    @pytest.mark.asyncio
    async def test_create_expense_share_success(self, mock_supabase, sample_expense_share_data):
        """Test successful expense share creation"""
        from app.crud.expense_shares import ExpenseSharesCRUD

        # Setup: Mock the entire chain and set the final result
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            sample_expense_share_data]

        # Test
        crud = ExpenseSharesCRUD(mock_supabase)
        result = await crud.create_expense_share(
            expense_id=sample_expense_share_data["expense_id"],
            user_id=sample_expense_share_data["user_id"],
            amount_owned=str(sample_expense_share_data["amount_owned"])
        )

        # Assertions
        assert result is not None
        assert str(result.expense_id) == sample_expense_share_data["expense_id"]
        assert str(result.user_id) == sample_expense_share_data["user_id"]
        assert result.amount_owned == sample_expense_share_data["amount_owned"]

        # Verify the mock chain was called correctly
        mock_supabase.table.assert_called_with('expense_shares')
        mock_supabase.table.return_value.insert.assert_called_once()
        mock_supabase.table.return_value.insert.return_value.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_expense_share_success(self, mock_supabase, sample_expense_share_data):
        """Test successful expense share retrieval by ID"""
        from app.crud.expense_shares import ExpenseSharesCRUD

        # Setup: Mock the select().eq().execute() chain
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_expense_share_data]

        # Test
        crud = ExpenseSharesCRUD(mock_supabase)
        result = await crud.get_expense_share_by_id(sample_expense_share_data["id"])

        # Assertions
        assert result is not None
        assert str(result.id) == sample_expense_share_data["id"]
        assert str(result.expense_id) == sample_expense_share_data["expense_id"]
        assert str(result.user_id) == sample_expense_share_data["user_id"]

        # Verify calls
        mock_supabase.table.assert_called_with('expense_shares')
        mock_supabase.table.return_value.select.assert_called_with('*')
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with(
            'id', sample_expense_share_data["id"])

    @pytest.mark.asyncio
    async def test_get_expense_shares_by_expense_success(self, mock_supabase, multiple_expense_shares):
        """Test successful retrieval of expense shares by expense"""
        from app.crud.expense_shares import ExpenseSharesCRUD

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.execute.return_value.data = multiple_expense_shares

        # Test
        crud = ExpenseSharesCRUD(mock_supabase)
        result = await crud.get_expense_shares_by_expense(multiple_expense_shares[0]["expense_id"])

        # Assertions
        assert len(result) == len(multiple_expense_shares)
        assert all(hasattr(share, 'amount_owned') for share in result)
        assert all(hasattr(share, 'user_id') for share in result)

        # Verify calls
        mock_supabase.table.assert_called_with('expense_shares')
        mock_supabase.table.return_value.select.assert_called_with('*')
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with(
            'expense_id', multiple_expense_shares[0]["expense_id"])

    @pytest.mark.asyncio
    async def test_get_expense_shares_by_user_success(self, mock_supabase, multiple_expense_shares):
        """Test successful retrieval of expense shares by user"""
        from app.crud.expense_shares import ExpenseSharesCRUD

        # Filter shares by user
        user_id = multiple_expense_shares[0]["user_id"]
        user_shares = [share for share in multiple_expense_shares if share["user_id"] == user_id]

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = user_shares

        # Test
        crud = ExpenseSharesCRUD(mock_supabase)
        result = await crud.get_expense_shares_by_user(user_id)

        # Assertions
        assert len(result) == len(user_shares)
        assert all(str(share.user_id) == user_id for share in result)

        # Verify calls
        mock_supabase.table.assert_called_with('expense_shares')
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with(
            'user_id', user_id)

    @pytest.mark.asyncio
    async def test_get_unsettled_shares_by_user_success(self, mock_supabase, multiple_expense_shares):
        """Test successful retrieval of unsettled expense shares by user"""
        from app.crud.expense_shares import ExpenseSharesCRUD

        # Filter unsettled shares by user
        user_id = multiple_expense_shares[0]["user_id"]
        unsettled_shares = [share for share in multiple_expense_shares 
                          if share["user_id"] == user_id and not share["is_settled"]]

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = unsettled_shares

        # Test
        crud = ExpenseSharesCRUD(mock_supabase)
        result = await crud.get_unsettled_shares_by_user(user_id)

        # Assertions
        assert len(result) == len(unsettled_shares)
        assert all(str(share.user_id) == user_id for share in result)
        assert all(not share.is_settled for share in result)

        # Verify calls - expect two .eq() calls for user_id and is_settled
        mock_supabase.table.assert_called_with('expense_shares')

    @pytest.mark.asyncio
    async def test_update_expense_share_success(self, mock_supabase, sample_expense_share_data):
        """Test successful expense share update"""
        from app.crud.expense_shares import ExpenseSharesCRUD

        # Setup: Mock update chain
        updated_data = sample_expense_share_data.copy()
        updated_data["is_settled"] = True
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            updated_data]

        # Test
        crud = ExpenseSharesCRUD(mock_supabase)
        result = await crud.update_expense_share(
            sample_expense_share_data["id"], 
            is_settled=True
        )

        # Assertions
        assert result is not None
        assert result.is_settled is True

        # Verify calls
        mock_supabase.table.assert_called_with('expense_shares')
        mock_supabase.table.return_value.update.assert_called_once()
        mock_supabase.table.return_value.update.return_value.eq.assert_called_with(
            'id', sample_expense_share_data["id"])

    @pytest.mark.asyncio
    async def test_settle_expense_share_success(self, mock_supabase, sample_expense_share_data):
        """Test successful expense share settlement"""
        from app.crud.expense_shares import ExpenseSharesCRUD

        # Setup: Mock update chain
        settled_data = sample_expense_share_data.copy()
        settled_data["is_settled"] = True
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            settled_data]

        # Test
        crud = ExpenseSharesCRUD(mock_supabase)
        result = await crud.settle_expense_share(sample_expense_share_data["id"])

        # Assertions
        assert result is not None
        assert result.is_settled is True

    @pytest.mark.asyncio
    async def test_delete_expense_share_success(self, mock_supabase, sample_expense_share_data):
        """Test successful expense share deletion"""
        from app.crud.expense_shares import ExpenseSharesCRUD

        # Setup: Mock delete chain
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [
            sample_expense_share_data]

        # Test
        crud = ExpenseSharesCRUD(mock_supabase)
        result = await crud.delete_expense_share(sample_expense_share_data["id"])

        # Assertions
        assert result is True

        # Verify calls
        mock_supabase.table.assert_called_with('expense_shares')
        mock_supabase.table.return_value.delete.return_value.eq.assert_called_with(
            'id', sample_expense_share_data["id"])

    @pytest.mark.asyncio
    async def test_delete_expense_shares_by_expense_success(self, mock_supabase, sample_expense_share_data):
        """Test successful deletion of all expense shares for an expense"""
        from app.crud.expense_shares import ExpenseSharesCRUD

        # Setup: Mock delete chain
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = []

        # Test
        crud = ExpenseSharesCRUD(mock_supabase)
        result = await crud.delete_expense_shares_by_expense(sample_expense_share_data["expense_id"])

        # Assertions - method always returns True for bulk deletes
        assert result is True

        # Verify calls
        mock_supabase.table.assert_called_with('expense_shares')
        mock_supabase.table.return_value.delete.return_value.eq.assert_called_with(
            'expense_id', sample_expense_share_data["expense_id"])


class TestExpenseSharesAPI:
    """Test ExpenseShares API endpoints using MagicMock"""

    @pytest.mark.asyncio
    async def test_create_expense_share_success(self, async_client: AsyncClient, mock_supabase, sample_expense_share_data):
        """Test successful expense share creation via API"""
        # Setup: Mock create_expense_share success
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            sample_expense_share_data]

        # Test
        response = await async_client.post(
            "/api/v1/expense_shares/",
            params={
                "expense_id": sample_expense_share_data["expense_id"],
                "user_id": sample_expense_share_data["user_id"],
                "amount_owned": str(sample_expense_share_data["amount_owned"])
            }
        )

        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["expense_id"] == sample_expense_share_data["expense_id"]
        assert data["user_id"] == sample_expense_share_data["user_id"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_expense_share_success(self, async_client: AsyncClient, mock_supabase, sample_expense_share_data):
        """Test successful expense share retrieval via API"""
        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_expense_share_data]

        # Test
        share_id = sample_expense_share_data["id"]
        response = await async_client.get(f"/api/v1/expense_shares/{share_id}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == share_id
        assert data["expense_id"] == sample_expense_share_data["expense_id"]

    @pytest.mark.asyncio
    async def test_get_expense_shares_by_expense(self, async_client: AsyncClient, mock_supabase, multiple_expense_shares):
        """Test get expense shares by expense via API"""
        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.execute.return_value.data = multiple_expense_shares

        # Test
        expense_id = multiple_expense_shares[0]["expense_id"]
        response = await async_client.get(f"/api/v1/expense_shares/expense/{expense_id}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(multiple_expense_shares)
        assert all("amount_owned" in share for share in data)

    @pytest.mark.asyncio
    async def test_get_expense_shares_by_user(self, async_client: AsyncClient, mock_supabase, multiple_expense_shares):
        """Test get expense shares by user via API"""
        # Filter shares by user
        user_id = multiple_expense_shares[0]["user_id"]
        user_shares = [share for share in multiple_expense_shares if share["user_id"] == user_id]
        
        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = user_shares

        # Test
        response = await async_client.get(f"/api/v1/expense_shares/user/{user_id}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(user_shares)
        assert all(share["user_id"] == user_id for share in data)

    @pytest.mark.asyncio
    async def test_get_unsettled_shares_by_user(self, async_client: AsyncClient, mock_supabase, multiple_expense_shares):
        """Test get unsettled expense shares by user via API"""
        # Filter unsettled shares by user
        user_id = multiple_expense_shares[0]["user_id"]
        unsettled_shares = [share for share in multiple_expense_shares 
                          if share["user_id"] == user_id and not share["is_settled"]]
        
        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = unsettled_shares

        # Test
        response = await async_client.get(f"/api/v1/expense_shares/user/{user_id}/unsettled")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(unsettled_shares)
        assert all(share["user_id"] == user_id for share in data)
        assert all(not share["is_settled"] for share in data)

    @pytest.mark.asyncio
    async def test_settle_expense_share_success(self, async_client: AsyncClient, mock_supabase, sample_expense_share_data):
        """Test successful expense share settlement via API"""
        # Setup: First call to check if share exists
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_expense_share_data]

        # Setup: Second call for settlement
        settled_data = sample_expense_share_data.copy()
        settled_data["is_settled"] = True
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            settled_data]

        # Test
        share_id = sample_expense_share_data["id"]
        response = await async_client.put(f"/api/v1/expense_shares/{share_id}/settle")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["is_settled"] is True

    @pytest.mark.asyncio
    async def test_get_expense_share_not_found(self, async_client: AsyncClient, mock_supabase):
        """Test expense share retrieval when share doesn't exist"""
        # Setup: Mock returns empty data
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Test
        response = await async_client.get("/api/v1/expense_shares/nonexistent-id")

        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_expense_share_success(self, async_client: AsyncClient, mock_supabase, sample_expense_share_data):
        """Test successful expense share deletion via API"""
        # Setup: First call to check if share exists
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_expense_share_data]

        # Setup: Second call for deletion
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [
            sample_expense_share_data]

        # Test
        share_id = sample_expense_share_data["id"]
        response = await async_client.delete(f"/api/v1/expense_shares/{share_id}")

        # Assertions
        assert response.status_code == 204


class TestExpenseSharesCrudEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.mark.asyncio
    async def test_get_expense_shares_by_expense_database_error(self, mock_supabase):
        """Test get expense shares by expense when database throws an error"""
        from app.crud.expense_shares import ExpenseSharesCRUD

        # Setup: Mock raises an exception
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.side_effect = Exception(
            "Database error")

        # Test
        crud = ExpenseSharesCRUD(mock_supabase)
        result = await crud.get_expense_shares_by_expense("expense-id")

        # Assertions - should return empty list on error
        assert result == []

    @pytest.mark.asyncio
    async def test_create_expense_share_failure(self, mock_supabase):
        """Test expense share creation failure when database returns no data"""
        from app.crud.expense_shares import ExpenseSharesCRUD

        # Setup: Mock returns None/empty data
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = None

        # Test
        crud = ExpenseSharesCRUD(mock_supabase)
        result = await crud.create_expense_share(
            expense_id=str(uuid.uuid4()),
            user_id=str(uuid.uuid4()),
            amount_owned="10.00"
        )

        # Assertions
        assert result is None