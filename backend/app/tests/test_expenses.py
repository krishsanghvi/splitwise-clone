import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import uuid
from datetime import datetime, date
from decimal import Decimal


class TestExpensesCrud:
    """Test ExpensesCRUD class directly using MagicMock"""

    @pytest.mark.asyncio
    async def test_create_expense_success(self, mock_supabase, sample_expense_data):
        """Test successful expense creation"""
        from app.crud.expenses import ExpensesCRUD

        # Setup: Mock the entire chain and set the final result
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            sample_expense_data]

        # Test
        crud = ExpensesCRUD(mock_supabase)
        result = await crud.create_expense(
            group_id=sample_expense_data["group_id"],
            paid_by=sample_expense_data["paid_by"],
            amount=str(sample_expense_data["amount"]),
            description=sample_expense_data["description"],
            split_method=sample_expense_data["split_method"],
            expense_date=date.fromisoformat(sample_expense_data["expense_date"])
        )

        # Assertions
        assert result is not None
        assert str(result.group_id) == sample_expense_data["group_id"]
        assert str(result.paid_by) == sample_expense_data["paid_by"]
        assert result.description == sample_expense_data["description"]

        # Verify the mock chain was called correctly
        mock_supabase.table.assert_called_with('expenses')
        mock_supabase.table.return_value.insert.assert_called_once()
        mock_supabase.table.return_value.insert.return_value.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_expense_success(self, mock_supabase, sample_expense_data):
        """Test successful expense retrieval by ID"""
        from app.crud.expenses import ExpensesCRUD

        # Setup: Mock the select().eq().execute() chain
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_expense_data]

        # Test
        crud = ExpensesCRUD(mock_supabase)
        result = await crud.get_expense_by_id(sample_expense_data["id"])

        # Assertions
        assert result is not None
        assert str(result.id) == sample_expense_data["id"]
        assert result.description == sample_expense_data["description"]
        assert str(result.group_id) == sample_expense_data["group_id"]

        # Verify calls
        mock_supabase.table.assert_called_with('expenses')
        mock_supabase.table.return_value.select.assert_called_with('*')
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with(
            'id', sample_expense_data["id"])

    @pytest.mark.asyncio
    async def test_get_expenses_by_group_success(self, mock_supabase, multiple_expenses):
        """Test successful retrieval of expenses by group"""
        from app.crud.expenses import ExpensesCRUD

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_expenses

        # Test
        crud = ExpensesCRUD(mock_supabase)
        result = await crud.get_expenses_by_group(multiple_expenses[0]["group_id"])

        # Assertions
        assert len(result) == len(multiple_expenses)
        assert all(hasattr(expense, 'description') for expense in result)
        assert all(hasattr(expense, 'amount') for expense in result)

        # Verify calls
        mock_supabase.table.assert_called_with('expenses')
        mock_supabase.table.return_value.select.assert_called_with('*')
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with(
            'group_id', multiple_expenses[0]["group_id"])

    @pytest.mark.asyncio
    async def test_get_expenses_by_user_success(self, mock_supabase, multiple_expenses):
        """Test successful retrieval of expenses by user"""
        from app.crud.expenses import ExpensesCRUD

        # Filter expenses by paid_by
        user_id = multiple_expenses[0]["paid_by"]
        user_expenses = [exp for exp in multiple_expenses if exp["paid_by"] == user_id]

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = user_expenses

        # Test
        crud = ExpensesCRUD(mock_supabase)
        result = await crud.get_expenses_by_user(user_id)

        # Assertions
        assert len(result) == len(user_expenses)
        assert all(str(expense.paid_by) == user_id for expense in result)

        # Verify calls
        mock_supabase.table.assert_called_with('expenses')
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with(
            'paid_by', user_id)

    @pytest.mark.asyncio
    async def test_update_expense_success(self, mock_supabase, sample_expense_data):
        """Test successful expense update"""
        from app.crud.expenses import ExpensesCRUD

        # Setup: Mock update chain
        updated_data = sample_expense_data.copy()
        updated_data["description"] = "Updated Description"
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            updated_data]

        # Test
        crud = ExpensesCRUD(mock_supabase)
        result = await crud.update_expense(
            sample_expense_data["id"], 
            description="Updated Description"
        )

        # Assertions
        assert result is not None
        assert result.description == "Updated Description"

        # Verify calls
        mock_supabase.table.assert_called_with('expenses')
        mock_supabase.table.return_value.update.assert_called_once()
        mock_supabase.table.return_value.update.return_value.eq.assert_called_with(
            'id', sample_expense_data["id"])

    @pytest.mark.asyncio
    async def test_delete_expense_success(self, mock_supabase, sample_expense_data):
        """Test successful expense deletion"""
        from app.crud.expenses import ExpensesCRUD

        # Setup: Mock delete chain
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [
            sample_expense_data]

        # Test
        crud = ExpensesCRUD(mock_supabase)
        result = await crud.delete_expense(sample_expense_data["id"])

        # Assertions
        assert result is True

        # Verify calls
        mock_supabase.table.assert_called_with('expenses')
        mock_supabase.table.return_value.delete.return_value.eq.assert_called_with(
            'id', sample_expense_data["id"])

    @pytest.mark.asyncio
    async def test_get_expenses_by_date_range_success(self, mock_supabase, multiple_expenses):
        """Test successful retrieval of expenses by date range"""
        from app.crud.expenses import ExpensesCRUD

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value.data = multiple_expenses

        # Test
        crud = ExpensesCRUD(mock_supabase)
        start_date = date(2023, 1, 1)
        end_date = date(2023, 12, 31)
        result = await crud.get_expenses_by_date_range(
            multiple_expenses[0]["group_id"], start_date, end_date
        )

        # Assertions
        assert len(result) == len(multiple_expenses)

        # Verify calls
        mock_supabase.table.assert_called_with('expenses')
        mock_chain.select.return_value.eq.return_value.gte.assert_called_with(
            'expense_date', start_date.isoformat())
        mock_chain.select.return_value.eq.return_value.gte.return_value.lte.assert_called_with(
            'expense_date', end_date.isoformat())


class TestExpensesAPI:
    """Test Expenses API endpoints using MagicMock"""

    @pytest.mark.asyncio
    async def test_create_expense_success(self, async_client: AsyncClient, mock_supabase, sample_expense_data):
        """Test successful expense creation via API"""
        # Setup: Mock create_expense success
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            sample_expense_data]

        # Test
        response = await async_client.post(
            "/api/v1/expenses/",
            params={
                "group_id": sample_expense_data["group_id"],
                "paid_by": sample_expense_data["paid_by"],
                "amount": str(sample_expense_data["amount"]),
                "description": sample_expense_data["description"],
                "split_method": sample_expense_data["split_method"],
                "expense_date": sample_expense_data["expense_date"]
            }
        )

        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == sample_expense_data["description"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_expense_success(self, async_client: AsyncClient, mock_supabase, sample_expense_data):
        """Test successful expense retrieval via API"""
        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_expense_data]

        # Test
        expense_id = sample_expense_data["id"]
        response = await async_client.get(f"/api/v1/expenses/{expense_id}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == expense_id
        assert data["description"] == sample_expense_data["description"]

    @pytest.mark.asyncio
    async def test_get_expenses_by_group(self, async_client: AsyncClient, mock_supabase, multiple_expenses):
        """Test get expenses by group via API"""
        # Setup the complete mock chain for get_expenses_by_group
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_expenses

        # Test
        group_id = multiple_expenses[0]["group_id"]
        response = await async_client.get(f"/api/v1/expenses/group/{group_id}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(multiple_expenses)
        assert all("description" in expense for expense in data)

    @pytest.mark.asyncio
    async def test_get_expenses_by_user(self, async_client: AsyncClient, mock_supabase, multiple_expenses):
        """Test get expenses by user via API"""
        # Filter expenses by user
        user_id = multiple_expenses[0]["paid_by"]
        user_expenses = [exp for exp in multiple_expenses if exp["paid_by"] == user_id]
        
        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = user_expenses

        # Test
        response = await async_client.get(f"/api/v1/expenses/user/{user_id}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(user_expenses)
        assert all(expense["paid_by"] == user_id for expense in data)

    @pytest.mark.asyncio
    async def test_get_expense_not_found(self, async_client: AsyncClient, mock_supabase):
        """Test expense retrieval when expense doesn't exist"""
        # Setup: Mock returns empty data
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Test
        response = await async_client.get("/api/v1/expenses/nonexistent-id")

        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_expense_success(self, async_client: AsyncClient, mock_supabase, sample_expense_data):
        """Test successful expense update via API"""
        # Setup: First call to check if expense exists
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_expense_data]

        # Setup: Second call for update
        updated_data = sample_expense_data.copy()
        updated_data["description"] = "Updated Description"
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            updated_data]

        # Test
        expense_id = sample_expense_data["id"]
        response = await async_client.put(
            f"/api/v1/expenses/{expense_id}",
            params={"description": "Updated Description"}
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated Description"

    @pytest.mark.asyncio
    async def test_delete_expense_success(self, async_client: AsyncClient, mock_supabase, sample_expense_data):
        """Test successful expense deletion via API"""
        # Setup: First call to check if expense exists
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_expense_data]

        # Setup: Second call for deletion
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [
            sample_expense_data]

        # Test
        expense_id = sample_expense_data["id"]
        response = await async_client.delete(f"/api/v1/expenses/{expense_id}")

        # Assertions
        assert response.status_code == 204


class TestExpensesCrudEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.mark.asyncio
    async def test_get_expenses_by_group_database_error(self, mock_supabase):
        """Test get expenses by group when database throws an error"""
        from app.crud.expenses import ExpensesCRUD

        # Setup: Mock raises an exception
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.side_effect = Exception(
            "Database error")

        # Test
        crud = ExpensesCRUD(mock_supabase)
        result = await crud.get_expenses_by_group("group-id")

        # Assertions - should return empty list on error
        assert result == []

    @pytest.mark.asyncio
    async def test_create_expense_failure(self, mock_supabase):
        """Test expense creation failure when database returns no data"""
        from app.crud.expenses import ExpensesCRUD

        # Setup: Mock returns None/empty data
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = None

        # Test
        crud = ExpensesCRUD(mock_supabase)
        result = await crud.create_expense(
            group_id=str(uuid.uuid4()),
            paid_by=str(uuid.uuid4()),
            amount="10.00",
            description="Test Expense",
            split_method="equal",
            expense_date=date.today()
        )

        # Assertions
        assert result is None