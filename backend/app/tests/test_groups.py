import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import uuid
from datetime import datetime


# =====================================================
# Group CRUD Tests
# =====================================================


class TestGroupCrud:
    """Test GroupCRUD class directly using MagicMock"""

    @pytest.mark.asyncio
    async def test_create_group_success(self, mock_supabase, sample_group_data):
        """Test successful group creation"""
        from app.crud.groups import GroupCRUD

        # Setup: Mock the entire chain and set the final result
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            sample_group_data]

        # Test
        crud = GroupCRUD(mock_supabase)
        result = await crud.create_group(
            created_by=sample_group_data["created_by"],
            name="Test Group",
            description="Test Description",
            invite_code="TEST123"
        )

        # Assertions
        assert result is not None
        assert result.group_name == "Test Group"
        assert result.group_description == "Test Description"
        assert result.invite_code == "TEST123"
        assert result.is_active is True

        # Verify the mock chain was called correctly
        mock_supabase.table.assert_called_with('groups')
        mock_supabase.table.return_value.insert.assert_called_once()
        mock_supabase.table.return_value.insert.return_value.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_group_failure(self, mock_supabase):
        """Test group creation failure when database returns no data"""
        from app.crud.groups import GroupCRUD

        # Setup: Mock returns None/empty data
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = None

        # Test
        crud = GroupCRUD(mock_supabase)
        result = await crud.create_group(
            created_by=str(uuid.uuid4()),
            name="Test Group"
        )

        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_get_group_by_id_success(self, mock_supabase, sample_group_data):
        """Test successful group retrieval by ID"""
        from app.crud.groups import GroupCRUD

        # Setup: Mock the select().eq().eq().execute() chain
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_data]

        # Test
        crud = GroupCRUD(mock_supabase)
        result = await crud.get_group_by_id(sample_group_data["id"])

        # Assertions
        assert result is not None
        assert str(result.id) == sample_group_data["id"]
        assert result.group_name == sample_group_data["group_name"]
        assert result.group_description == sample_group_data["group_description"]

        # Verify calls
        mock_supabase.table.assert_called_with('groups')
        mock_supabase.table.return_value.select.assert_called_with('*')

    @pytest.mark.asyncio
    async def test_get_group_by_id_not_found(self, mock_supabase):
        """Test group retrieval when group doesn't exist"""
        from app.crud.groups import GroupCRUD

        # Setup: Mock returns empty data
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        # Test
        crud = GroupCRUD(mock_supabase)
        result = await crud.get_group_by_id("nonexistent-id")

        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_get_group_by_invite_code_success(self, mock_supabase, sample_group_data):
        """Test successful group retrieval by invite code"""
        from app.crud.groups import GroupCRUD

        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_data]

        # Test
        crud = GroupCRUD(mock_supabase)
        result = await crud.get_group_by_invite_code(sample_group_data["invite_code"])

        # Assertions
        assert result is not None
        assert result.invite_code == sample_group_data["invite_code"]
        assert result.group_name == sample_group_data["group_name"]

    @pytest.mark.asyncio
    async def test_get_groups_by_user_success(self, mock_supabase, multiple_groups):
        """Test successful retrieval of groups by user"""
        from app.crud.groups import GroupCRUD

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_groups

        # Test
        crud = GroupCRUD(mock_supabase)
        result = await crud.get_groups_by_user(multiple_groups[0]["created_by"])

        # Assertions
        assert len(result) == len(multiple_groups)
        assert all(hasattr(group, 'group_name') for group in result)
        assert all(hasattr(group, 'created_by') for group in result)

        # Verify calls
        mock_supabase.table.assert_called_with('groups')
        mock_supabase.table.return_value.select.assert_called_with('*')

    @pytest.mark.asyncio
    async def test_get_all_groups_success(self, mock_supabase, multiple_groups):
        """Test successful retrieval of all groups"""
        from app.crud.groups import GroupCRUD

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_groups

        # Test
        crud = GroupCRUD(mock_supabase)
        result = await crud.get_all_groups()

        # Assertions
        assert len(result) == len(multiple_groups)
        assert all(hasattr(group, 'group_name') for group in result)
        assert all(group.is_active for group in result)

    @pytest.mark.asyncio
    async def test_get_all_groups_with_pagination(self, mock_supabase, multiple_groups):
        """Test get all groups with custom pagination"""
        from app.crud.groups import GroupCRUD

        # Setup
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_groups[
            :2]

        # Test with custom limit and offset
        crud = GroupCRUD(mock_supabase)
        result = await crud.get_all_groups(limit=2, offset=10)

        # Assertions
        assert len(result) == 2

        # Verify pagination parameters
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.assert_called_with(
            10, 11)  # offset=10, limit=2

    @pytest.mark.asyncio
    async def test_update_group_success(self, mock_supabase, sample_group_data):
        """Test successful group update"""
        from app.crud.groups import GroupCRUD

        # Setup: Mock the update chain
        updated_data = sample_group_data.copy()
        updated_data["group_name"] = "Updated Group Name"
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            updated_data]

        # Test
        crud = GroupCRUD(mock_supabase)
        result = await crud.update_group(
            group_id=sample_group_data["id"],
            name="Updated Group Name"
        )

        # Assertions
        assert result is not None
        assert result.group_name == "Updated Group Name"

        # Verify calls
        mock_supabase.table.assert_called_with('groups')
        mock_supabase.table.return_value.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_group_no_changes(self, mock_supabase, sample_group_data):
        """Test group update with no changes returns current group"""
        from app.crud.groups import GroupCRUD

        # Setup: Mock get_group_by_id for no-changes scenario
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_data]

        # Test
        crud = GroupCRUD(mock_supabase)
        result = await crud.update_group(group_id=sample_group_data["id"])

        # Assertions
        assert result is not None
        assert result.group_name == sample_group_data["group_name"]

    @pytest.mark.asyncio
    async def test_delete_group_success(self, mock_supabase):
        """Test successful group soft delete"""
        from app.crud.groups import GroupCRUD

        # Setup: Mock the update chain for soft delete
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {"id": "test-id", "is_active": False}]

        # Test
        crud = GroupCRUD(mock_supabase)
        result = await crud.delete_group("test-id")

        # Assertions
        assert result is True

        # Verify calls
        mock_supabase.table.assert_called_with('groups')
        mock_supabase.table.return_value.update.assert_called_with({'is_active': False})

    @pytest.mark.asyncio
    async def test_search_groups_success(self, mock_supabase, multiple_groups):
        """Test successful group search using RPC"""
        from app.crud.groups import GroupCRUD

        # Setup: Mock the rpc call
        filtered_groups = [
            group for group in multiple_groups if "1" in group["group_name"]]
        mock_supabase.rpc.return_value.execute.return_value.data = filtered_groups

        # Test
        crud = GroupCRUD(mock_supabase)
        result = await crud.search_groups("Group 1")

        # Assertions
        assert len(result) == 1
        assert "1" in result[0].group_name

        # Verify calls
        mock_supabase.rpc.assert_called_with("search_groups", {"term": "Group 1", "max_limit": 20})


# =====================================================
# Group API Tests
# =====================================================


class TestGroupAPI:
    """Test Group API endpoints using MagicMock"""

    @pytest.mark.asyncio
    async def test_create_group_success(self, async_client: AsyncClient, mock_supabase, sample_group_data):
        """Test successful group creation via API"""
        # Setup: Mock get_group_by_invite_code (no existing group) and create_group (success)
        # First call: get_group_by_invite_code returns empty (no existing group)
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        # Second call: create_group returns the created group
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            sample_group_data]

        # Test
        response = await async_client.post(
            "/api/v1/groups/",
            params={
                "created_by": sample_group_data["created_by"],
                "name": "Test Group",
                "description": "Test Description",
                "invite_code": "TEST123"
            }
        )

        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["group_name"] == "Test Group"
        assert data["group_description"] == "Test Description"
        assert data["invite_code"] == "TEST123"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_group_duplicate_invite_code(self, async_client: AsyncClient, mock_supabase, sample_group_data):
        """Test group creation with duplicate invite code"""
        # Setup: Mock get_group_by_invite_code returns existing group
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_data]

        # Test
        response = await async_client.post(
            "/api/v1/groups/",
            params={
                "created_by": sample_group_data["created_by"],
                "name": "Test Group",
                "invite_code": "TEST123"
            }
        )

        # Assertions
        assert response.status_code == 400
        assert "already in use" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_group_success(self, async_client: AsyncClient, mock_supabase, sample_group_data):
        """Test successful group retrieval via API"""
        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_data]

        # Test
        group_id = sample_group_data["id"]
        response = await async_client.get(f"/api/v1/groups/id/{group_id}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == group_id
        assert data["group_name"] == sample_group_data["group_name"]

    @pytest.mark.asyncio
    async def test_get_group_not_found(self, async_client: AsyncClient, mock_supabase):
        """Test group retrieval when group doesn't exist"""
        # Setup: Mock returns empty data
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        # Test
        response = await async_client.get("/api/v1/groups/id/nonexistent-id")

        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_group_by_invite_code_success(self, async_client: AsyncClient, mock_supabase, sample_group_data):
        """Test successful group retrieval by invite code via API"""
        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_data]

        # Test
        response = await async_client.get(f"/api/v1/groups/invite/{sample_group_data['invite_code']}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["invite_code"] == sample_group_data["invite_code"]
        assert data["group_name"] == sample_group_data["group_name"]

    @pytest.mark.asyncio
    async def test_get_all_groups(self, async_client: AsyncClient, mock_supabase, multiple_groups):
        """Test get all groups via API"""
        # Setup the complete mock chain for get_all_groups
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_groups

        # Test
        response = await async_client.get("/api/v1/groups/")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("group_name" in group for group in data)

    @pytest.mark.asyncio
    async def test_get_all_groups_with_pagination(self, async_client: AsyncClient, mock_supabase, multiple_groups):
        """Test get all groups with pagination parameters"""
        # Setup
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_groups[
            :2]

        # Test
        response = await async_client.get("/api/v1/groups/?limit=2&offset=10")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_get_groups_by_user(self, async_client: AsyncClient, mock_supabase, multiple_groups):
        """Test get groups by user via API"""
        # Setup
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_groups

        # Test
        user_id = multiple_groups[0]["created_by"]
        response = await async_client.get(f"/api/v1/groups/user/{user_id}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(group["created_by"] == user_id for group in data)

    @pytest.mark.asyncio
    async def test_update_group_success(self, async_client: AsyncClient, mock_supabase, sample_group_data):
        """Test successful group update via API"""
        # Setup: Mock get_group_by_id (group exists) and update_group (success)
        # First call: get_group_by_id returns existing group
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_data]

        # Second call: update_group returns updated group
        updated_data = sample_group_data.copy()
        updated_data["group_name"] = "Updated Group Name"
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            updated_data]

        # Test
        response = await async_client.put(
            f"/api/v1/groups/{sample_group_data['id']}",
            params={
                "name": "Updated Group Name"
            }
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["group_name"] == "Updated Group Name"

    @pytest.mark.asyncio
    async def test_update_group_not_found(self, async_client: AsyncClient, mock_supabase):
        """Test group update when group doesn't exist"""
        # Setup: Mock returns empty data for group lookup
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        # Test
        response = await async_client.put(
            "/api/v1/groups/nonexistent-id",
            params={"name": "Updated Name"}
        )

        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_group_success(self, async_client: AsyncClient, mock_supabase, sample_group_data):
        """Test successful group deletion via API"""
        # Setup: Mock get_group_by_id (group exists) and delete_group (success)
        # First call: get_group_by_id returns existing group
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_data]

        # Second call: delete_group (soft delete) returns success
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {"id": sample_group_data["id"]}]

        # Test
        response = await async_client.delete(f"/api/v1/groups/{sample_group_data['id']}")

        # Assertions
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_group_not_found(self, async_client: AsyncClient, mock_supabase):
        """Test group deletion when group doesn't exist"""
        # Setup: Mock returns empty data for group lookup
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        # Test
        response = await async_client.delete("/api/v1/groups/nonexistent-id")

        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_search_groups(self, async_client: AsyncClient, mock_supabase, multiple_groups):
        """Test group search via API"""
        # Setup: Mock returns filtered results
        filtered_groups = [
            group for group in multiple_groups if "1" in group["group_name"]]
        # Mock the rpc call that the CRUD actually uses
        mock_supabase.rpc.return_value.execute.return_value.data = filtered_groups

        # Test
        response = await async_client.get("/api/v1/groups/search?search_term=Group 1")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "1" in data[0]["group_name"]


# =====================================================
# Edge Cases and Error Scenarios
# =====================================================


class TestGroupCrudEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.mark.asyncio
    async def test_get_all_groups_database_error(self, mock_supabase):
        """Test get all groups when database throws an error"""
        from app.crud.groups import GroupCRUD

        # Setup: Mock raises an exception
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.side_effect = Exception(
            "Database error")

        # Test
        crud = GroupCRUD(mock_supabase)
        result = await crud.get_all_groups()

        # Assertions - should return empty list on error
        assert result == []

    @pytest.mark.asyncio
    async def test_search_groups_empty_result(self, mock_supabase):
        """Test search groups when no matches found"""
        from app.crud.groups import GroupCRUD

        # Setup: Mock returns empty/None data
        mock_supabase.rpc.return_value.execute.return_value.data = None

        # Test
        crud = GroupCRUD(mock_supabase)
        result = await crud.search_groups("nonexistent")

        # Assertions
        assert result == []

    @pytest.mark.asyncio
    async def test_create_group_database_exception(self, mock_supabase):
        """Test group creation when database throws an exception"""
        from app.crud.groups import GroupCRUD

        # Setup: Mock raises an exception
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception(
            "Database error")

        # Test
        crud = GroupCRUD(mock_supabase)
        result = await crud.create_group(
            created_by=str(uuid.uuid4()),
            name="Test Group"
        )

        # Assertions
        assert result is None