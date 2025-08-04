import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock
import uuid
from datetime import datetime


# =====================================================
# Group Member CRUD Tests
# =====================================================


class TestGroupMemberCrud:
    """Test GroupMemberCRUD class directly using MagicMock"""

    @pytest.mark.asyncio
    async def test_add_member_success(self, mock_supabase, sample_group_member_data):
        """Test successful member addition"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup: Mock the entire chain and set the final result
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            sample_group_member_data]

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.add_member(
            group_id=sample_group_member_data["group_id"],
            user_id=sample_group_member_data["user_id"],
            role="member"
        )

        # Assertions
        assert result is not None
        assert result.role == "member"
        assert result.is_active is True
        assert str(result.group_id) == sample_group_member_data["group_id"]
        assert str(result.user_id) == sample_group_member_data["user_id"]

        # Verify the mock chain was called correctly
        mock_supabase.table.assert_called_with('group_members')
        mock_supabase.table.return_value.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_member_failure(self, mock_supabase):
        """Test member addition failure when database returns no data"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup: Mock returns None/empty data
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = None

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.add_member(
            group_id=str(uuid.uuid4()),
            user_id=str(uuid.uuid4())
        )

        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_get_member_by_id_success(self, mock_supabase, sample_group_member_data):
        """Test successful member retrieval by ID"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup: Mock the select().eq().eq().execute() chain
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_member_data]

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.get_member_by_id(sample_group_member_data["id"])

        # Assertions
        assert result is not None
        assert str(result.id) == sample_group_member_data["id"]
        assert str(result.group_id) == sample_group_member_data["group_id"]
        assert str(result.user_id) == sample_group_member_data["user_id"]

        # Verify calls
        mock_supabase.table.assert_called_with('group_members')
        mock_supabase.table.return_value.select.assert_called_with('*')

    @pytest.mark.asyncio
    async def test_get_member_by_id_not_found(self, mock_supabase):
        """Test member retrieval when member doesn't exist"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup: Mock returns empty data
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.get_member_by_id("nonexistent-id")

        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_get_member_by_user_and_group_success(self, mock_supabase, sample_group_member_data):
        """Test successful member retrieval by user and group"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_member_data]

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.get_member_by_user_and_group(
            sample_group_member_data["group_id"],
            sample_group_member_data["user_id"]
        )

        # Assertions
        assert result is not None
        assert str(result.group_id) == sample_group_member_data["group_id"]
        assert str(result.user_id) == sample_group_member_data["user_id"]

    @pytest.mark.asyncio
    async def test_get_group_members_success(self, mock_supabase, multiple_group_members):
        """Test successful retrieval of group members"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_group_members

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.get_group_members(multiple_group_members[0]["group_id"])

        # Assertions
        assert len(result) == len(multiple_group_members)
        assert all(hasattr(member, 'role') for member in result)
        assert all(member.is_active for member in result)

        # Verify calls
        mock_supabase.table.assert_called_with('group_members')
        mock_supabase.table.return_value.select.assert_called_with('*')

    @pytest.mark.asyncio
    async def test_get_user_groups_success(self, mock_supabase, multiple_group_members):
        """Test successful retrieval of user groups"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = [
            multiple_group_members[0]]

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.get_user_groups(multiple_group_members[0]["user_id"])

        # Assertions
        assert len(result) == 1
        assert str(result[0].user_id) == multiple_group_members[0]["user_id"]

    @pytest.mark.asyncio
    async def test_update_member_role_success(self, mock_supabase, sample_group_member_data):
        """Test successful member role update"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup: Mock the update chain
        updated_data = sample_group_member_data.copy()
        updated_data["role"] = "admin"
        mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            updated_data]

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.update_member_role(
            member_id=sample_group_member_data["id"],
            role="admin"
        )

        # Assertions
        assert result is not None
        assert result.role == "admin"

        # Verify calls
        mock_supabase.table.assert_called_with('group_members')
        mock_supabase.table.return_value.update.assert_called_with({'role': 'admin'})

    @pytest.mark.asyncio
    async def test_remove_member_success(self, mock_supabase):
        """Test successful member removal (soft delete)"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup: Mock the update chain for soft delete
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {"id": "test-id", "is_active": False}]

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.remove_member("test-id")

        # Assertions
        assert result is True

        # Verify calls
        mock_supabase.table.assert_called_with('group_members')
        mock_supabase.table.return_value.update.assert_called_with({'is_active': False})

    @pytest.mark.asyncio
    async def test_remove_member_by_user_and_group_success(self, mock_supabase):
        """Test successful member removal by user and group"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup: Mock the update chain
        mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"id": "test-id"}]

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.remove_member_by_user_and_group("group-id", "user-id")

        # Assertions
        assert result is True

    @pytest.mark.asyncio
    async def test_is_member_true(self, mock_supabase):
        """Test membership check returns true"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup: Mock returns data (member exists)
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"id": "member-id"}]

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.is_member("group-id", "user-id")

        # Assertions
        assert result is True

    @pytest.mark.asyncio
    async def test_is_member_false(self, mock_supabase):
        """Test membership check returns false"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup: Mock returns empty data
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.is_member("group-id", "user-id")

        # Assertions
        assert result is False

    @pytest.mark.asyncio
    async def test_is_admin_true(self, mock_supabase):
        """Test admin check returns true"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup: Mock returns admin role
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "admin"}]

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.is_admin("group-id", "user-id")

        # Assertions
        assert result is True

    @pytest.mark.asyncio
    async def test_is_admin_false(self, mock_supabase):
        """Test admin check returns false for regular member"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup: Mock returns member role
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "member"}]

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.is_admin("group-id", "user-id")

        # Assertions
        assert result is False

    @pytest.mark.asyncio
    async def test_get_group_admins_success(self, mock_supabase, admin_group_member_data):
        """Test successful retrieval of group admins"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.in_.return_value.eq.return_value.execute.return_value.data = [
            admin_group_member_data]

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.get_group_admins(admin_group_member_data["group_id"])

        # Assertions
        assert len(result) == 1
        assert result[0].role == "admin"


# =====================================================
# Group Member API Tests
# =====================================================


class TestGroupMemberAPI:
    """Test Group Member API endpoints using MagicMock"""

    @pytest.mark.asyncio
    async def test_add_member_success(self, async_client: AsyncClient, mock_supabase, sample_group_member_data):
        """Test successful member addition via API"""
        # Setup: Mock get_member_by_user_and_group (no existing member) and add_member (success)
        # First call: get_member_by_user_and_group returns empty (no existing member)
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        # Second call: add_member returns the created member
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            sample_group_member_data]

        # Test
        response = await async_client.post(
            "/api/v1/group_members/",
            params={
                "group_id": sample_group_member_data["group_id"],
                "user_id": sample_group_member_data["user_id"],
                "role": "member"
            }
        )

        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "member"
        assert data["group_id"] == sample_group_member_data["group_id"]
        assert data["user_id"] == sample_group_member_data["user_id"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_add_member_already_exists(self, async_client: AsyncClient, mock_supabase, sample_group_member_data):
        """Test member addition when user is already a member"""
        # Setup: Mock get_member_by_user_and_group returns existing member
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_member_data]

        # Test
        response = await async_client.post(
            "/api/v1/group_members/",
            params={
                "group_id": sample_group_member_data["group_id"],
                "user_id": sample_group_member_data["user_id"]
            }
        )

        # Assertions
        assert response.status_code == 400
        assert "already a member" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_member_success(self, async_client: AsyncClient, mock_supabase, sample_group_member_data):
        """Test successful member retrieval via API"""
        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_member_data]

        # Test
        member_id = sample_group_member_data["id"]
        response = await async_client.get(f"/api/v1/group_members/member/{member_id}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == member_id
        assert data["group_id"] == sample_group_member_data["group_id"]

    @pytest.mark.asyncio
    async def test_get_member_not_found(self, async_client: AsyncClient, mock_supabase):
        """Test member retrieval when member doesn't exist"""
        # Setup: Mock returns empty data
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        # Test
        response = await async_client.get("/api/v1/group_members/member/nonexistent-id")

        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_member_by_user_and_group_success(self, async_client: AsyncClient, mock_supabase, sample_group_member_data):
        """Test successful member retrieval by user and group via API"""
        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_member_data]

        # Test
        response = await async_client.get(
            f"/api/v1/group_members/group/{sample_group_member_data['group_id']}/member/{sample_group_member_data['user_id']}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["group_id"] == sample_group_member_data["group_id"]
        assert data["user_id"] == sample_group_member_data["user_id"]

    @pytest.mark.asyncio
    async def test_get_group_members(self, async_client: AsyncClient, mock_supabase, multiple_group_members):
        """Test get group members via API"""
        # Setup the complete mock chain for get_group_members
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_group_members

        # Test
        group_id = multiple_group_members[0]["group_id"]
        response = await async_client.get(f"/api/v1/group_members/group/{group_id}/members")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        assert all("role" in member for member in data)

    @pytest.mark.asyncio
    async def test_get_user_groups(self, async_client: AsyncClient, mock_supabase, multiple_group_members):
        """Test get user groups via API"""
        # Setup
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = [
            multiple_group_members[0]]

        # Test
        user_id = multiple_group_members[0]["user_id"]
        response = await async_client.get(f"/api/v1/group_members/user/{user_id}/groups")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == user_id

    @pytest.mark.asyncio
    async def test_get_group_admins(self, async_client: AsyncClient, mock_supabase, admin_group_member_data):
        """Test get group admins via API"""
        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.in_.return_value.eq.return_value.execute.return_value.data = [
            admin_group_member_data]

        # Test
        group_id = admin_group_member_data["group_id"]
        response = await async_client.get(f"/api/v1/group_members/group/{group_id}/admins")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["role"] == "admin"

    @pytest.mark.asyncio
    async def test_update_member_role_success(self, async_client: AsyncClient, mock_supabase, sample_group_member_data):
        """Test successful member role update via API"""
        # Setup: Mock get_member_by_id (member exists) and update_member_role (success)
        # First call: get_member_by_id returns existing member
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_member_data]

        # Second call: update_member_role returns updated member
        updated_data = sample_group_member_data.copy()
        updated_data["role"] = "admin"
        mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            updated_data]

        # Test
        response = await async_client.put(
            f"/api/v1/group_members/member/{sample_group_member_data['id']}/role",
            params={"role": "admin"}
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"

    @pytest.mark.asyncio
    async def test_update_member_role_invalid_role(self, async_client: AsyncClient, mock_supabase, sample_group_member_data):
        """Test member role update with invalid role"""
        # Setup: Mock get_member_by_id returns existing member
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_member_data]

        # Test
        response = await async_client.put(
            f"/api/v1/group_members/member/{sample_group_member_data['id']}/role",
            params={"role": "invalid_role"}
        )

        # Assertions
        assert response.status_code == 400
        assert "Invalid role" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_remove_member_success(self, async_client: AsyncClient, mock_supabase, sample_group_member_data):
        """Test successful member removal via API"""
        # Setup: Mock get_member_by_id (member exists) and remove_member (success)
        # First call: get_member_by_id returns existing member
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_member_data]

        # Second call: remove_member (soft delete) returns success
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {"id": sample_group_member_data["id"]}]

        # Test
        response = await async_client.delete(f"/api/v1/group_members/member/{sample_group_member_data['id']}")

        # Assertions
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_remove_member_not_found(self, async_client: AsyncClient, mock_supabase):
        """Test member removal when member doesn't exist"""
        # Setup: Mock returns empty data for member lookup
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        # Test
        response = await async_client.delete("/api/v1/group_members/member/nonexistent-id")

        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_remove_member_from_group_success(self, async_client: AsyncClient, mock_supabase, sample_group_member_data):
        """Test successful member removal from group via API"""
        # Setup: Mock get_member_by_user_and_group (member exists) and remove_member_by_user_and_group (success)
        # First call: get_member_by_user_and_group returns existing member
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            sample_group_member_data]

        # Second call: remove_member_by_user_and_group returns success
        mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"id": sample_group_member_data["id"]}]

        # Test
        response = await async_client.delete(
            f"/api/v1/group_members/group/{sample_group_member_data['group_id']}/member/{sample_group_member_data['user_id']}")

        # Assertions
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_check_membership(self, async_client: AsyncClient, mock_supabase):
        """Test membership check via API"""
        # Setup: Mock is_member and is_admin calls
        # First call for is_member
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"id": "member-id"}]

        # Create a fresh mock for the second call
        mock_supabase.reset_mock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "admin"}]

        # Test
        response = await async_client.get("/api/v1/group_members/group/group-id/member/user-id/check")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "is_member" in data
        assert "is_admin" in data


# =====================================================
# Edge Cases and Error Scenarios
# =====================================================


class TestGroupMemberCrudEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.mark.asyncio
    async def test_get_group_members_database_error(self, mock_supabase):
        """Test get group members when database throws an error"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup: Mock raises an exception
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute.side_effect = Exception(
            "Database error")

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.get_group_members("group-id")

        # Assertions - should return empty list on error
        assert result == []

    @pytest.mark.asyncio
    async def test_add_member_database_exception(self, mock_supabase):
        """Test member addition when database throws an exception"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup: Mock raises an exception
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception(
            "Database error")

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.add_member(
            group_id=str(uuid.uuid4()),
            user_id=str(uuid.uuid4())
        )

        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_is_member_database_exception(self, mock_supabase):
        """Test membership check when database throws an exception"""
        from app.crud.group_members import GroupMemberCRUD

        # Setup: Mock raises an exception
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.side_effect = Exception(
            "Database error")

        # Test
        crud = GroupMemberCRUD(mock_supabase)
        result = await crud.is_member("group-id", "user-id")

        # Assertions
        assert result is False