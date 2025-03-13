"""Tests for the resource manager."""

import pytest
from typing import Dict

from virtuallife.environment.resources import ResourceManager
from virtuallife.types import Position


@pytest.fixture
def resource_manager() -> ResourceManager:
    """Create a resource manager for testing."""
    return ResourceManager()


@pytest.fixture
def populated_resource_manager() -> ResourceManager:
    """Create a resource manager with some resources."""
    manager = ResourceManager()
    manager.add_resource("food", (10, 20), 100)
    manager.add_resource("water", (30, 40), 50)
    manager.add_resource("wood", (10, 20), 75)
    return manager


def test_add_resource(resource_manager: ResourceManager):
    """Test that resources can be added."""
    # Arrange
    resource_type = "food"
    position: Position = (10, 20)
    amount = 100
    
    # Act
    resource_manager.add_resource(resource_type, position, amount)
    
    # Assert
    assert resource_manager.get_resource_amount(resource_type, position) == amount


def test_add_resource_increments_existing(resource_manager: ResourceManager):
    """Test that adding a resource to an existing position increments the amount."""
    # Arrange
    resource_type = "food"
    position: Position = (10, 20)
    initial_amount = 100
    additional_amount = 50
    
    resource_manager.add_resource(resource_type, position, initial_amount)
    
    # Act
    resource_manager.add_resource(resource_type, position, additional_amount)
    
    # Assert
    assert resource_manager.get_resource_amount(resource_type, position) == initial_amount + additional_amount


def test_remove_resource(populated_resource_manager: ResourceManager):
    """Test that resources can be removed."""
    # Arrange
    resource_type = "food"
    position: Position = (10, 20)
    
    # Act
    populated_resource_manager.remove_resource(resource_type, position)
    
    # Assert
    assert populated_resource_manager.get_resource_amount(resource_type, position) == 0
    assert resource_type not in populated_resource_manager.get_resources_at_position(position)


def test_remove_nonexistent_resource(resource_manager: ResourceManager):
    """Test that removing a nonexistent resource has no effect."""
    # Arrange
    resource_type = "food"
    position: Position = (10, 20)
    
    # Act
    resource_manager.remove_resource(resource_type, position)
    
    # Assert
    assert resource_manager.get_resource_amount(resource_type, position) == 0


def test_get_resource_amount(populated_resource_manager: ResourceManager):
    """Test that resource amounts can be retrieved."""
    # Arrange
    resource_type = "food"
    position: Position = (10, 20)
    
    # Act
    result = populated_resource_manager.get_resource_amount(resource_type, position)
    
    # Assert
    assert result == 100


def test_get_nonexistent_resource_amount(resource_manager: ResourceManager):
    """Test that retrieving a nonexistent resource amount returns 0."""
    # Arrange
    resource_type = "food"
    position: Position = (10, 20)
    
    # Act
    result = resource_manager.get_resource_amount(resource_type, position)
    
    # Assert
    assert result == 0


def test_get_resources_at_position(populated_resource_manager: ResourceManager):
    """Test that all resources at a position can be retrieved."""
    # Arrange
    position: Position = (10, 20)
    
    # Act
    result = populated_resource_manager.get_resources_at_position(position)
    
    # Assert
    assert len(result) == 2
    assert result["food"] == 100
    assert result["wood"] == 75


def test_get_resources_at_empty_position(resource_manager: ResourceManager):
    """Test that retrieving resources at an empty position returns an empty dict."""
    # Arrange
    position: Position = (10, 20)
    
    # Act
    result = resource_manager.get_resources_at_position(position)
    
    # Assert
    assert isinstance(result, dict)
    assert len(result) == 0


def test_get_resource_positions(populated_resource_manager: ResourceManager):
    """Test that resource positions can be retrieved."""
    # Arrange
    resource_type = "food"
    
    # Act
    result = populated_resource_manager.get_resource_positions(resource_type)
    
    # Assert
    assert len(result) == 1
    assert (10, 20) in result


def test_get_nonexistent_resource_positions(resource_manager: ResourceManager):
    """Test that retrieving positions for a nonexistent resource returns an empty list."""
    # Arrange
    resource_type = "food"
    
    # Act
    result = resource_manager.get_resource_positions(resource_type)
    
    # Assert
    assert isinstance(result, list)
    assert len(result) == 0


def test_consume_resource(populated_resource_manager: ResourceManager):
    """Test that resources can be consumed."""
    # Arrange
    resource_type = "food"
    position: Position = (10, 20)
    amount = 30
    
    # Act
    consumed = populated_resource_manager.consume_resource(resource_type, position, amount)
    
    # Assert
    assert consumed == amount
    assert populated_resource_manager.get_resource_amount(resource_type, position) == 70


def test_consume_more_than_available(populated_resource_manager: ResourceManager):
    """Test that consuming more than available consumes all available."""
    # Arrange
    resource_type = "food"
    position: Position = (10, 20)
    amount = 150
    
    # Act
    consumed = populated_resource_manager.consume_resource(resource_type, position, amount)
    
    # Assert
    assert consumed == 100
    assert populated_resource_manager.get_resource_amount(resource_type, position) == 0


def test_consume_nonexistent_resource(resource_manager: ResourceManager):
    """Test that consuming a nonexistent resource returns 0."""
    # Arrange
    resource_type = "food"
    position: Position = (10, 20)
    amount = 30
    
    # Act
    consumed = resource_manager.consume_resource(resource_type, position, amount)
    
    # Assert
    assert consumed == 0


def test_update_resource(populated_resource_manager: ResourceManager):
    """Test that resources can be updated."""
    # Arrange
    resource_type = "food"
    position: Position = (10, 20)
    new_amount = 50
    
    # Act
    populated_resource_manager.update_resource(resource_type, position, new_amount)
    
    # Assert
    assert populated_resource_manager.get_resource_amount(resource_type, position) == new_amount


def test_update_resource_to_zero(populated_resource_manager: ResourceManager):
    """Test that updating a resource to 0 removes it."""
    # Arrange
    resource_type = "food"
    position: Position = (10, 20)
    
    # Act
    populated_resource_manager.update_resource(resource_type, position, 0)
    
    # Assert
    assert populated_resource_manager.get_resource_amount(resource_type, position) == 0
    assert resource_type not in populated_resource_manager.get_resources_at_position(position)


def test_update_nonexistent_resource(resource_manager: ResourceManager):
    """Test that updating a nonexistent resource creates it."""
    # Arrange
    resource_type = "food"
    position: Position = (10, 20)
    amount = 50
    
    # Act
    resource_manager.update_resource(resource_type, position, amount)
    
    # Assert
    assert resource_manager.get_resource_amount(resource_type, position) == amount


def test_transfer_resource(populated_resource_manager: ResourceManager):
    """Test that resources can be transferred."""
    # Arrange
    resource_type = "food"
    from_position: Position = (10, 20)
    to_position: Position = (30, 40)
    amount = 30
    
    # Act
    transferred = populated_resource_manager.transfer_resource(
        resource_type, from_position, to_position, amount
    )
    
    # Assert
    assert transferred == amount
    assert populated_resource_manager.get_resource_amount(resource_type, from_position) == 70
    assert populated_resource_manager.get_resource_amount(resource_type, to_position) == 30


def test_transfer_more_than_available(populated_resource_manager: ResourceManager):
    """Test that transferring more than available transfers all available."""
    # Arrange
    resource_type = "food"
    from_position: Position = (10, 20)
    to_position: Position = (30, 40)
    amount = 150
    
    # Act
    transferred = populated_resource_manager.transfer_resource(
        resource_type, from_position, to_position, amount
    )
    
    # Assert
    assert transferred == 100
    assert populated_resource_manager.get_resource_amount(resource_type, from_position) == 0
    assert populated_resource_manager.get_resource_amount(resource_type, to_position) == 100


def test_transfer_nonexistent_resource(resource_manager: ResourceManager):
    """Test that transferring a nonexistent resource transfers nothing."""
    # Arrange
    resource_type = "food"
    from_position: Position = (10, 20)
    to_position: Position = (30, 40)
    amount = 30
    
    # Act
    transferred = resource_manager.transfer_resource(
        resource_type, from_position, to_position, amount
    )
    
    # Assert
    assert transferred == 0
    assert resource_manager.get_resource_amount(resource_type, from_position) == 0
    assert resource_manager.get_resource_amount(resource_type, to_position) == 0


def test_get_all_resource_types(populated_resource_manager: ResourceManager):
    """Test that all resource types can be retrieved."""
    # Act
    result = populated_resource_manager.get_all_resource_types()
    
    # Assert
    assert len(result) == 3
    assert "food" in result
    assert "water" in result
    assert "wood" in result


def test_get_total_resource_amount(populated_resource_manager: ResourceManager):
    """Test that the total amount of a resource can be retrieved."""
    # Arrange
    populated_resource_manager.add_resource("food", (30, 40), 50)
    
    # Act
    result = populated_resource_manager.get_total_resource_amount("food")
    
    # Assert
    assert result == 150


def test_get_total_nonexistent_resource_amount(resource_manager: ResourceManager):
    """Test that the total amount of a nonexistent resource is 0."""
    # Act
    result = resource_manager.get_total_resource_amount("food")
    
    # Assert
    assert result == 0


def test_clear(populated_resource_manager: ResourceManager):
    """Test that all resources can be cleared."""
    # Act
    populated_resource_manager.clear()
    
    # Assert
    assert len(populated_resource_manager.get_all_resource_types()) == 0


def test_clear_resource_type(populated_resource_manager: ResourceManager):
    """Test that a specific resource type can be cleared."""
    # Act
    populated_resource_manager.clear_resource_type("food")
    
    # Assert
    assert "food" not in populated_resource_manager.get_all_resource_types()
    assert "water" in populated_resource_manager.get_all_resource_types()
    assert "wood" in populated_resource_manager.get_all_resource_types() 