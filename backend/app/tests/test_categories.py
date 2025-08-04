import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock
import uuid
from datetime import datetime


# =====================================================
# Category CRUD Tests
# =====================================================


class TestCategoryCrud:
    """Test CategoryCRUD class directly using MagicMock"""

    @pytest.mark.asyncio
    async def test_create_category_success(self, mock_supabase, sample_category_data):
        """Test successful category creation"""
        from app.crud.categories import CategoryCRUD

        # Setup: Mock the entire chain and set the final result
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            sample_category_data]

        # Test
        crud = CategoryCRUD(mock_supabase)
        result = await crud.create_category(
            name="Food & Dining",
            icon="utensils",
            color="#FF5733",
            is_default=True
        )

        # Assertions
        assert result is not None
        assert result.name == "Food & Dining"
        assert result.icon == "utensils"
        assert result.color == "#FF5733"
        assert result.is_default is True

        # Verify the mock chain was called correctly
        mock_supabase.table.assert_called_with('categories')
        mock_supabase.table.return_value.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_category_failure(self, mock_supabase):
        """Test category creation failure when database returns no data"""
        from app.crud.categories import CategoryCRUD

        # Setup: Mock returns None/empty data
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = None

        # Test
        crud = CategoryCRUD(mock_supabase)
        result = await crud.create_category(
            name="Test Category",
            icon="test",
            color="#000000"
        )

        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_get_category_by_id_success(self, mock_supabase, sample_category_data):
        """Test successful category retrieval by ID"""
        from app.crud.categories import CategoryCRUD

        # Setup: Mock the select().eq().execute() chain
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_category_data]

        # Test
        crud = CategoryCRUD(mock_supabase)
        result = await crud.get_category_by_id(sample_category_data["id"])

        # Assertions
        assert result is not None
        assert str(result.id) == sample_category_data["id"]
        assert result.name == sample_category_data["name"]
        assert result.icon == sample_category_data["icon"]

        # Verify calls
        mock_supabase.table.assert_called_with('categories')
        mock_supabase.table.return_value.select.assert_called_with('*')

    @pytest.mark.asyncio
    async def test_get_category_by_id_not_found(self, mock_supabase):
        """Test category retrieval when category doesn't exist"""
        from app.crud.categories import CategoryCRUD

        # Setup: Mock returns empty data
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Test
        crud = CategoryCRUD(mock_supabase)
        result = await crud.get_category_by_id("nonexistent-id")

        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_get_category_by_name_success(self, mock_supabase, sample_category_data):
        """Test successful category retrieval by name"""
        from app.crud.categories import CategoryCRUD

        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_category_data]

        # Test
        crud = CategoryCRUD(mock_supabase)
        result = await crud.get_category_by_name(sample_category_data["name"])

        # Assertions
        assert result is not None
        assert result.name == sample_category_data["name"]
        assert result.icon == sample_category_data["icon"]

    @pytest.mark.asyncio
    async def test_get_all_categories_success(self, mock_supabase, multiple_categories):
        """Test successful retrieval of all categories"""
        from app.crud.categories import CategoryCRUD

        # Setup the complete mock chain
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_categories

        # Test
        crud = CategoryCRUD(mock_supabase)
        result = await crud.get_all_categories()

        # Assertions
        assert len(result) == len(multiple_categories)
        assert all(hasattr(category, 'name') for category in result)
        assert all(hasattr(category, 'icon') for category in result)

        # Verify calls
        mock_supabase.table.assert_called_with('categories')
        mock_supabase.table.return_value.select.assert_called_with('*')

    @pytest.mark.asyncio
    async def test_get_all_categories_with_pagination(self, mock_supabase, multiple_categories):
        """Test get all categories with custom pagination"""
        from app.crud.categories import CategoryCRUD

        # Setup
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_categories[
            :2]

        # Test with custom limit and offset
        crud = CategoryCRUD(mock_supabase)
        result = await crud.get_all_categories(limit=2, offset=10)

        # Assertions
        assert len(result) == 2

        # Verify pagination parameters
        mock_supabase.table.return_value.select.return_value.order.return_value.range.assert_called_with(
            10, 11)  # offset=10, limit=2

    @pytest.mark.asyncio
    async def test_get_default_categories_success(self, mock_supabase, multiple_categories):
        """Test successful retrieval of default categories"""
        from app.crud.categories import CategoryCRUD

        # Setup: Filter to only default categories
        default_categories = [cat for cat in multiple_categories if cat["is_default"]]
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.execute.return_value.data = default_categories

        # Test
        crud = CategoryCRUD(mock_supabase)
        result = await crud.get_default_categories()

        # Assertions
        assert len(result) == len(default_categories)
        assert all(category.is_default for category in result)

        # Verify calls
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with('is_default', True)

    @pytest.mark.asyncio
    async def test_get_custom_categories_success(self, mock_supabase, multiple_categories):
        """Test successful retrieval of custom categories"""
        from app.crud.categories import CategoryCRUD

        # Setup: Filter to only custom categories
        custom_categories = [cat for cat in multiple_categories if not cat["is_default"]]
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.execute.return_value.data = custom_categories

        # Test
        crud = CategoryCRUD(mock_supabase)
        result = await crud.get_custom_categories()

        # Assertions
        assert len(result) == len(custom_categories)
        assert all(not category.is_default for category in result)

        # Verify calls
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with('is_default', False)

    @pytest.mark.asyncio
    async def test_update_category_success(self, mock_supabase, sample_category_data):
        """Test successful category update"""
        from app.crud.categories import CategoryCRUD

        # Setup: Mock the update chain
        updated_data = sample_category_data.copy()
        updated_data["name"] = "Updated Category Name"
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            updated_data]

        # Test
        crud = CategoryCRUD(mock_supabase)
        result = await crud.update_category(
            category_id=sample_category_data["id"],
            name="Updated Category Name"
        )

        # Assertions
        assert result is not None
        assert result.name == "Updated Category Name"

        # Verify calls
        mock_supabase.table.assert_called_with('categories')
        mock_supabase.table.return_value.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_category_no_changes(self, mock_supabase, sample_category_data):
        """Test category update with no changes returns current category"""
        from app.crud.categories import CategoryCRUD

        # Setup: Mock get_category_by_id for no-changes scenario
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_category_data]

        # Test
        crud = CategoryCRUD(mock_supabase)
        result = await crud.update_category(category_id=sample_category_data["id"])

        # Assertions
        assert result is not None
        assert result.name == sample_category_data["name"]

    @pytest.mark.asyncio
    async def test_delete_category_success(self, mock_supabase):
        """Test successful category deletion"""
        from app.crud.categories import CategoryCRUD

        # Setup: Mock the delete chain
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [
            {"id": "test-id"}]

        # Test
        crud = CategoryCRUD(mock_supabase)
        result = await crud.delete_category("test-id")

        # Assertions
        assert result is True

        # Verify calls
        mock_supabase.table.assert_called_with('categories')
        mock_supabase.table.return_value.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_categories_success(self, mock_supabase, multiple_categories):
        """Test successful category search"""
        from app.crud.categories import CategoryCRUD

        # Setup: Mock search results
        filtered_categories = [
            cat for cat in multiple_categories if "1" in cat["name"]]
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.ilike.return_value.order.return_value.limit.return_value.execute.return_value.data = filtered_categories

        # Test
        crud = CategoryCRUD(mock_supabase)
        result = await crud.search_categories("Category 1")

        # Assertions
        assert len(result) == 1
        assert "1" in result[0].name

        # Verify calls
        mock_supabase.table.return_value.select.return_value.ilike.assert_called_with('name', '%Category 1%')


# =====================================================
# Category API Tests
# =====================================================


class TestCategoryAPI:
    """Test Category API endpoints using MagicMock"""

    @pytest.mark.asyncio
    async def test_create_category_success(self, async_client: AsyncClient, mock_supabase, sample_category_data):
        """Test successful category creation via API"""
        # Setup: Mock get_category_by_name (no existing category) and create_category (success)
        # First call: get_category_by_name returns empty (no existing category)
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Second call: create_category returns the created category
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            sample_category_data]

        # Test
        response = await async_client.post(
            "/api/v1/categories/",
            params={
                "name": "Food & Dining",
                "icon": "utensils",
                "color": "#FF5733",
                "is_default": True
            }
        )

        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Food & Dining"
        assert data["icon"] == "utensils"
        assert data["color"] == "#FF5733"
        assert data["is_default"] is True
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_category_duplicate_name(self, async_client: AsyncClient, mock_supabase, sample_category_data):
        """Test category creation with duplicate name"""
        # Setup: Mock get_category_by_name returns existing category
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_category_data]

        # Test
        response = await async_client.post(
            "/api/v1/categories/",
            params={
                "name": "Food & Dining",
                "icon": "utensils",
                "color": "#FF5733"
            }
        )

        # Assertions
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_category_success(self, async_client: AsyncClient, mock_supabase, sample_category_data):
        """Test successful category retrieval via API"""
        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_category_data]

        # Test
        category_id = sample_category_data["id"]
        response = await async_client.get(f"/api/v1/categories/{category_id}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == sample_category_data["name"]

    @pytest.mark.asyncio
    async def test_get_category_not_found(self, async_client: AsyncClient, mock_supabase):
        """Test category retrieval when category doesn't exist"""
        # Setup: Mock returns empty data
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Test
        response = await async_client.get("/api/v1/categories/nonexistent-id")

        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_category_by_name_success(self, async_client: AsyncClient, mock_supabase, sample_category_data):
        """Test successful category retrieval by name via API"""
        # Setup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_category_data]

        # Test
        response = await async_client.get(f"/api/v1/categories/name/{sample_category_data['name']}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_category_data["name"]
        assert data["icon"] == sample_category_data["icon"]

    @pytest.mark.asyncio
    async def test_get_all_categories(self, async_client: AsyncClient, mock_supabase, multiple_categories):
        """Test get all categories via API"""
        # Setup the complete mock chain for get_all_categories
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_categories

        # Test
        response = await async_client.get("/api/v1/categories/")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        assert all("name" in category for category in data)

    @pytest.mark.asyncio
    async def test_get_all_categories_with_pagination(self, async_client: AsyncClient, mock_supabase, multiple_categories):
        """Test get all categories with pagination parameters"""
        # Setup
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.order.return_value.range.return_value.execute.return_value.data = multiple_categories[
            :2]

        # Test
        response = await async_client.get("/api/v1/categories/?limit=2&offset=10")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_get_default_categories(self, async_client: AsyncClient, mock_supabase, multiple_categories):
        """Test get default categories via API"""
        # Setup: Filter to only default categories
        default_categories = [cat for cat in multiple_categories if cat["is_default"]]
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.execute.return_value.data = default_categories

        # Test
        response = await async_client.get("/api/v1/categories/default/list")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Only categories 1 and 2 are default
        assert all(category["is_default"] for category in data)

    @pytest.mark.asyncio
    async def test_get_custom_categories(self, async_client: AsyncClient, mock_supabase, multiple_categories):
        """Test get custom categories via API"""
        # Setup: Filter to only custom categories
        custom_categories = [cat for cat in multiple_categories if not cat["is_default"]]
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.eq.return_value.order.return_value.execute.return_value.data = custom_categories

        # Test
        response = await async_client.get("/api/v1/categories/custom/list")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Categories 3 and 4 are custom
        assert all(not category["is_default"] for category in data)

    @pytest.mark.asyncio
    async def test_update_category_success(self, async_client: AsyncClient, mock_supabase, sample_category_data):
        """Test successful category update via API"""
        # Setup: Mock get_category_by_id (category exists) and update_category (success)
        # First call: get_category_by_id returns existing category
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_category_data]

        # Second call: update_category returns updated category
        updated_data = sample_category_data.copy()
        updated_data["name"] = "Updated Category Name"
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            updated_data]

        # Test
        response = await async_client.put(
            f"/api/v1/categories/{sample_category_data['id']}",
            params={
                "name": "Updated Category Name"
            }
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Category Name"

    @pytest.mark.asyncio
    async def test_update_category_not_found(self, async_client: AsyncClient, mock_supabase):
        """Test category update when category doesn't exist"""
        # Setup: Mock returns empty data for category lookup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Test
        response = await async_client.put(
            "/api/v1/categories/nonexistent-id",
            params={"name": "Updated Name"}
        )

        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_category_duplicate_name(self, async_client: AsyncClient, mock_supabase, sample_category_data):
        """Test category update with duplicate name"""
        # Setup: Create a different category with same name that we want to update to
        different_category = sample_category_data.copy()
        different_category["id"] = str(uuid.uuid4())
        different_category["name"] = "Existing Category Name"
        
        # Mock sequence: first call gets the category being updated, second call finds duplicate name
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            type('MockResult', (), {'data': [sample_category_data]})(),  # First call: get category being updated
            type('MockResult', (), {'data': [different_category]})()  # Second call: find duplicate name
        ]

        # Test
        response = await async_client.put(
            f"/api/v1/categories/{sample_category_data['id']}",
            params={"name": "Existing Category Name"}
        )

        # Assertions
        assert response.status_code == 400
        assert "already in use" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_delete_category_success(self, async_client: AsyncClient, mock_supabase, custom_category_data):
        """Test successful category deletion via API"""
        # Setup: Mock get_category_by_id (category exists) and delete_category (success)
        # First call: get_category_by_id returns existing custom category
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            custom_category_data]

        # Second call: delete_category returns success
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [
            {"id": custom_category_data["id"]}]

        # Test
        response = await async_client.delete(f"/api/v1/categories/{custom_category_data['id']}")

        # Assertions
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_category_not_found(self, async_client: AsyncClient, mock_supabase):
        """Test category deletion when category doesn't exist"""
        # Setup: Mock returns empty data for category lookup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Test
        response = await async_client.delete("/api/v1/categories/nonexistent-id")

        # Assertions
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_default_category_forbidden(self, async_client: AsyncClient, mock_supabase, sample_category_data):
        """Test deletion of default category is forbidden"""
        # Setup: Mock get_category_by_id returns default category
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            sample_category_data]  # This is a default category

        # Test
        response = await async_client.delete(f"/api/v1/categories/{sample_category_data['id']}")

        # Assertions
        assert response.status_code == 400
        assert "Cannot delete default" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_search_categories(self, async_client: AsyncClient, mock_supabase, multiple_categories):
        """Test category search via API"""
        # Setup: Mock returns filtered results
        filtered_categories = [
            cat for cat in multiple_categories if "1" in cat["name"]]
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.ilike.return_value.order.return_value.limit.return_value.execute.return_value.data = filtered_categories

        # Test
        response = await async_client.get("/api/v1/categories/search?search_term=Category 1")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "1" in data[0]["name"]


# =====================================================
# Edge Cases and Error Scenarios
# =====================================================


class TestCategoryCrudEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.mark.asyncio
    async def test_get_all_categories_database_error(self, mock_supabase):
        """Test get all categories when database throws an error"""
        from app.crud.categories import CategoryCRUD

        # Setup: Mock raises an exception
        mock_supabase.table.return_value.select.return_value.order.return_value.range.return_value.execute.side_effect = Exception(
            "Database error")

        # Test
        crud = CategoryCRUD(mock_supabase)
        result = await crud.get_all_categories()

        # Assertions - should return empty list on error
        assert result == []

    @pytest.mark.asyncio
    async def test_search_categories_empty_result(self, mock_supabase):
        """Test search categories when no matches found"""
        from app.crud.categories import CategoryCRUD

        # Setup: Mock returns empty data
        mock_chain = mock_supabase.table.return_value
        mock_chain.select.return_value.ilike.return_value.order.return_value.limit.return_value.execute.return_value.data = []

        # Test
        crud = CategoryCRUD(mock_supabase)
        result = await crud.search_categories("nonexistent")

        # Assertions
        assert result == []

    @pytest.mark.asyncio
    async def test_create_category_database_exception(self, mock_supabase):
        """Test category creation when database throws an exception"""
        from app.crud.categories import CategoryCRUD

        # Setup: Mock raises an exception
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception(
            "Database error")

        # Test
        crud = CategoryCRUD(mock_supabase)
        result = await crud.create_category(
            name="Test Category",
            icon="test",
            color="#000000"
        )

        # Assertions
        assert result is None