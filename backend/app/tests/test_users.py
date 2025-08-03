import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import uuid
from datetime import datetime


# =====================================================
# FIXED test_users.py - Correct Mock Chains
# =====================================================


class TestUserCrud:
    """Test UserCRUD class directly using MagicMock"""

    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_supabase, sample_user_data):
        """Test successful user creation"""
        from app.crud.users import UserCRUD

        # Setup: Mock the entire chain and set the final result
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            sample_user_data]

        # Test
        crud = UserCRUD(mock_supabase)
        result = await crud.create_user(
            email="test@example.com",
            full_name="Test User",
            timezone="UTC"
        )

        # Assertions
        assert result is not None
        assert result.email == "test@example.com"
        assert result.full_name == "Test User"
        assert result.timezone == "UTC"

        # Verify the mock chain was called correctly
        mock_supabase.table.assert_called_with('users')
        mock_supabase.table.return_value.insert.assert_called_once()
        mock_supabase.table.return_value.insert.return_value.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_success(self, mock_supabase, sample_user_data):
        """Test successful user retrieval by ID"""
        from app.crud.users import UserCRUD

        # Setup: Mock the select().eq().execute() chain
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_user_data]

        # Test
        crud = UserCRUD(mock_supabase)
        result = await crud.get_user_by_id(sample_user_data["id"])

        # Assertions
        assert result is not None
        assert str(result.id) == sample_user_data["id"]
        assert result.email == sample_user_data["email"]
        assert result.full_name == sample_user_data["full_name"]

        # Verify calls
        mock_supabase.table.assert_called_with('users')
        mock_supabase.table.return_value.select.assert_called_with('*')
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with(
            'id', sample_user_data["id"])

    @pytest.mark.asyncio
    async def test_get_all_users_success(self, mock_supabase, multiple_users):
        """Test successful retrieval of all users"""
        from app.crud.users import UserCRUD

        # FIXED: Setup the complete mock chain to match your actual method
        # Your method: .select('*').order('created_at', desc=True).range(offset, offset + limit - 1).execute()
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_users

        # Test
        crud = UserCRUD(mock_supabase)
        result = await crud.get_all_users()

        # Assertions
        assert len(result) == len(multiple_users)
        assert all(hasattr(user, 'email') for user in result)
        assert all(hasattr(user, 'full_name') for user in result)

        # Verify calls
        mock_supabase.table.assert_called_with('users')
        mock_supabase.table.return_value.select.assert_called_with('*')
        mock_supabase.table.return_value.select.return_value.order.assert_called_with(
            'created_at', desc=True)
        mock_supabase.table.return_value.select.return_value.order.return_value.range.assert_called_with(
            0, 49)  # offset=0, limit=50

    @pytest.mark.asyncio
    async def test_get_all_users_with_pagination(self, mock_supabase, multiple_users):
        """Test get all users with custom pagination"""
        from app.crud.users import UserCRUD

        # Setup
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_users[
            :2]

        # Test with custom limit and offset
        crud = UserCRUD(mock_supabase)
        result = await crud.get_all_users(limit=2, offset=10)

        # Assertions
        assert len(result) == 2

        # Verify pagination parameters
        mock_supabase.table.return_value.select.return_value.order.return_value.range.assert_called_with(
            10, 11)  # offset=10, limit=2

    @pytest.mark.asyncio
    async def test_get_all_users_empty(self, mock_supabase):
        """Test get all users when no users exist"""
        from app.crud.users import UserCRUD

        # Setup: Empty result
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.order.return_value.range.return_value.execute.return_value.data = []

        # Test
        crud = UserCRUD(mock_supabase)
        result = await crud.get_all_users()

        # Assertions
        assert result == []

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, mock_supabase, sample_user_data):
        """Test successful user retrieval by email"""
        from app.crud.users import UserCRUD

        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_user_data]

        # Test
        crud = UserCRUD(mock_supabase)
        result = await crud.get_user_by_email(sample_user_data["email"])

        # Assertions
        assert result is not None
        assert result.email == sample_user_data["email"]

        # Verify calls
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with(
            'email', sample_user_data["email"])

    @pytest.mark.asyncio
    async def test_search_users_success(self, mock_supabase, multiple_users):
        """Test successful user search"""
        from app.crud.users import UserCRUD

        # Setup: Mock returns filtered results
        # Your search method likely uses: .select('*').or_(query).limit(limit).execute()
        filtered_users = [
            user for user in multiple_users if "1" in user["email"]]
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.or_.return_value.limit.return_value.execute.return_value.data = filtered_users

        # Test
        crud = UserCRUD(mock_supabase)
        result = await crud.search_users("test1", limit=20)

        # Assertions
        assert len(result) == 1
        assert "test1" in result[0].email

        # Verify calls
        mock_supabase.table.return_value.select.return_value.or_.assert_called_once()
        mock_supabase.table.return_value.select.return_value.or_.return_value.limit.assert_called_with(
            20)


class TestUserAPI:
    """Test User API endpoints using MagicMock"""

    @pytest.mark.asyncio
    async def test_create_user_success(self, async_client: AsyncClient, mock_supabase, sample_user_data):
        """Test successful user creation via API"""
        # Setup: Mock get_user_by_email (no existing user) and create_user (success)
        # First call: get_user_by_email returns empty (no existing user)
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Second call: create_user returns the created user
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            sample_user_data]

        # Test
        response = await async_client.post(
            "/api/v1/users/",
            params={
                "email": "test@example.com",
                "full_name": "Test User",
                "timezone": "UTC"
            }
        )

        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, async_client: AsyncClient, mock_supabase, sample_user_data):
        """Test user creation with duplicate email"""
        # Setup: Mock get_user_by_email returns existing user
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_user_data]

        # Test
        response = await async_client.post(
            "/api/v1/users/",
            params={
                "email": "test@example.com",
                "full_name": "Test User"
            }
        )

        # Assertions
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_user_success(self, async_client: AsyncClient, mock_supabase, sample_user_data):
        """Test successful user retrieval via API"""
        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_user_data]

        # Test
        user_id = sample_user_data["id"]
        response = await async_client.get(f"/api/v1/users/{user_id}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == sample_user_data["email"]

    @pytest.mark.asyncio
    async def test_get_all_users(self, async_client: AsyncClient, mock_supabase, multiple_users):
        """Test get all users via API"""
        # FIXED: Setup the complete mock chain for get_all_users
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_users

        # Test
        response = await async_client.get("/api/v1/users/")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("email" in user for user in data)

    @pytest.mark.asyncio
    async def test_get_all_users_with_pagination(self, async_client: AsyncClient, mock_supabase, multiple_users):
        """Test get all users with pagination parameters"""
        # Setup
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_users[
            :2]

        # Test
        response = await async_client.get("/api/v1/users/?limit=2&offset=10")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, async_client: AsyncClient, mock_supabase):
        """Test user retrieval when user doesn't exist"""
        # Setup: Mock returns empty data
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Test
        response = await async_client.get("/api/v1/users/nonexistent-id")

        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_search_users(self, async_client: AsyncClient, mock_supabase, multiple_users):
        """Test user search via API"""
        # Setup: Mock returns filtered results
        filtered_users = [
            user for user in multiple_users if "1" in user["email"]]
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.or_.return_value.limit.return_value.execute.return_value.data = filtered_users

        # Test
        response = await async_client.get("/api/v1/users/search/?q=test1")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "test1" in data[0]["email"]


# =====================================================
# Additional Helper Tests for Edge Cases
# =====================================================

class TestUserCrudEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.mark.asyncio
    async def test_get_all_users_database_error(self, mock_supabase):
        """Test get all users when database throws an error"""
        from app.crud.users import UserCRUD

        # Setup: Mock raises an exception
        mock_supabase.table.return_value.select.return_value.order.return_value.range.return_value.execute.side_effect = Exception(
            "Database error")

        # Test
        crud = UserCRUD(mock_supabase)
        result = await crud.get_all_users()

        # Assertions - should return empty list on error
        assert result == []

    @pytest.mark.asyncio
    async def test_create_user_failure(self, mock_supabase):
        """Test user creation failure when database returns no data"""
        from app.crud.users import UserCRUD

        # Setup: Mock returns None/empty data
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = None

        # Test
        crud = UserCRUD(mock_supabase)
        result = await crud.create_user(
            email="test@example.com",
            full_name="Test User"
        )

        # Assertions
        assert result is None
