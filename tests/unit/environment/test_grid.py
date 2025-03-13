"""Tests for the spatial grid."""

import pytest
from typing import Tuple, Set, Dict, List
from uuid import UUID, uuid4

from virtuallife.environment.grid import SpatialGrid
from virtuallife.environment.boundary import WrappedBoundary, BoundedBoundary, InfiniteBoundary
from virtuallife.types import Position


@pytest.fixture
def wrapped_grid() -> SpatialGrid:
    """Create a spatial grid with wrapped boundary for testing."""
    return SpatialGrid(100, 100, WrappedBoundary(100, 100))


@pytest.fixture
def bounded_grid() -> SpatialGrid:
    """Create a spatial grid with bounded boundary for testing."""
    return SpatialGrid(100, 100, BoundedBoundary(100, 100))


@pytest.fixture
def infinite_grid() -> SpatialGrid:
    """Create a spatial grid with infinite boundary for testing."""
    return SpatialGrid(100, 100, InfiniteBoundary(100, 100))


@pytest.fixture
def entity_ids() -> List[UUID]:
    """Create a list of entity IDs for testing."""
    return [uuid4() for _ in range(10)]


def test_add_entity(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that entities can be added to the grid."""
    # Arrange
    entity_id = entity_ids[0]
    position: Position = (10, 20)
    
    # Act
    wrapped_grid.add_entity(entity_id, position)
    
    # Assert
    assert entity_id in wrapped_grid
    assert wrapped_grid.get_entity_position(entity_id) == position
    assert entity_id in wrapped_grid.get_entities_at_position(position)


def test_add_entity_outside_grid(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that entities outside the grid are normalized when added."""
    # Arrange
    entity_id = entity_ids[0]
    position: Position = (110, 120)
    
    # Act
    wrapped_grid.add_entity(entity_id, position)
    
    # Assert
    assert entity_id in wrapped_grid
    assert wrapped_grid.get_entity_position(entity_id) == (10, 20)
    assert entity_id in wrapped_grid.get_entities_at_position((10, 20))


def test_remove_entity(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that entities can be removed from the grid."""
    # Arrange
    entity_id = entity_ids[0]
    position: Position = (10, 20)
    wrapped_grid.add_entity(entity_id, position)
    
    # Act
    wrapped_grid.remove_entity(entity_id)
    
    # Assert
    assert entity_id not in wrapped_grid
    assert wrapped_grid.get_entity_position(entity_id) is None
    assert entity_id not in wrapped_grid.get_entities_at_position(position)


def test_remove_entity_with_position(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that entities can be removed from the grid with a position."""
    # Arrange
    entity_id = entity_ids[0]
    position: Position = (10, 20)
    wrapped_grid.add_entity(entity_id, position)
    
    # Act
    wrapped_grid.remove_entity(entity_id, position)
    
    # Assert
    assert entity_id not in wrapped_grid
    assert wrapped_grid.get_entity_position(entity_id) is None
    assert entity_id not in wrapped_grid.get_entities_at_position(position)


def test_remove_nonexistent_entity(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that removing a nonexistent entity has no effect."""
    # Arrange
    entity_id = entity_ids[0]
    
    # Act
    wrapped_grid.remove_entity(entity_id)
    
    # Assert
    assert entity_id not in wrapped_grid
    assert wrapped_grid.get_entity_position(entity_id) is None


def test_update_entity_position(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that entity positions can be updated."""
    # Arrange
    entity_id = entity_ids[0]
    old_position: Position = (10, 20)
    new_position: Position = (30, 40)
    wrapped_grid.add_entity(entity_id, old_position)
    
    # Act
    wrapped_grid.update_entity_position(entity_id, new_position)
    
    # Assert
    assert wrapped_grid.get_entity_position(entity_id) == new_position
    assert entity_id not in wrapped_grid.get_entities_at_position(old_position)
    assert entity_id in wrapped_grid.get_entities_at_position(new_position)


def test_update_nonexistent_entity_position(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that updating a nonexistent entity position adds the entity."""
    # Arrange
    entity_id = entity_ids[0]
    position: Position = (10, 20)
    
    # Act
    wrapped_grid.update_entity_position(entity_id, position)
    
    # Assert
    assert entity_id in wrapped_grid
    assert wrapped_grid.get_entity_position(entity_id) == position
    assert entity_id in wrapped_grid.get_entities_at_position(position)


def test_get_entity_position(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that entity positions can be retrieved."""
    # Arrange
    entity_id = entity_ids[0]
    position: Position = (10, 20)
    wrapped_grid.add_entity(entity_id, position)
    
    # Act
    result = wrapped_grid.get_entity_position(entity_id)
    
    # Assert
    assert result == position


def test_get_nonexistent_entity_position(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that retrieving a nonexistent entity position returns None."""
    # Arrange
    entity_id = entity_ids[0]
    
    # Act
    result = wrapped_grid.get_entity_position(entity_id)
    
    # Assert
    assert result is None


def test_get_entities_at_position(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that entities at a position can be retrieved."""
    # Arrange
    entity_id1 = entity_ids[0]
    entity_id2 = entity_ids[1]
    position: Position = (10, 20)
    other_position: Position = (30, 40)
    wrapped_grid.add_entity(entity_id1, position)
    wrapped_grid.add_entity(entity_id2, position)
    wrapped_grid.add_entity(entity_ids[2], other_position)
    
    # Act
    result = wrapped_grid.get_entities_at_position(position)
    
    # Assert
    assert len(result) == 2
    assert entity_id1 in result
    assert entity_id2 in result
    assert entity_ids[2] not in result


def test_get_entities_at_empty_position(wrapped_grid: SpatialGrid):
    """Test that retrieving entities at an empty position returns an empty set."""
    # Act
    result = wrapped_grid.get_entities_at_position((10, 20))
    
    # Assert
    assert isinstance(result, set)
    assert len(result) == 0


def test_get_entities_in_radius(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that entities within a radius can be retrieved."""
    # Arrange
    positions = [(10, 20), (12, 22), (14, 23), (30, 40)]
    for i, position in enumerate(positions):
        wrapped_grid.add_entity(entity_ids[i], position)
    
    # Act
    result = wrapped_grid.get_entities_in_radius((10, 20), 5)
    
    # Assert
    assert len(result) == 3
    assert entity_ids[0] in result  # (10, 20)
    assert entity_ids[1] in result  # (12, 22)
    assert entity_ids[2] in result  # (14, 23)
    assert entity_ids[3] not in result  # (30, 40)


def test_get_entities_in_empty_radius(wrapped_grid: SpatialGrid):
    """Test that retrieving entities in an empty radius returns an empty set."""
    # Act
    result = wrapped_grid.get_entities_in_radius((10, 20), 5)
    
    # Assert
    assert isinstance(result, set)
    assert len(result) == 0


def test_get_entities_in_rectangle(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that entities within a rectangle can be retrieved."""
    # Arrange
    positions = [(10, 20), (15, 25), (5, 15), (30, 40)]
    for i, position in enumerate(positions):
        wrapped_grid.add_entity(entity_ids[i], position)
    
    # Act
    result = wrapped_grid.get_entities_in_rectangle((5, 15), (20, 30))
    
    # Assert
    assert len(result) == 3
    assert entity_ids[0] in result  # (10, 20)
    assert entity_ids[1] in result  # (15, 25)
    assert entity_ids[2] in result  # (5, 15)
    assert entity_ids[3] not in result  # (30, 40)


def test_get_nearest_entities(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that the nearest entities can be retrieved."""
    # Arrange
    positions = [(10, 20), (12, 22), (15, 25), (30, 40)]
    for i, position in enumerate(positions):
        wrapped_grid.add_entity(entity_ids[i], position)
    
    # Act
    result = wrapped_grid.get_nearest_entities((10, 20), 2)
    
    # Assert
    assert len(result) == 2
    assert result[0][0] == entity_ids[0]  # (10, 20)
    assert result[1][0] == entity_ids[1]  # (12, 22)


def test_get_nearest_entities_with_count_greater_than_available(
    wrapped_grid: SpatialGrid, entity_ids: List[UUID]
):
    """Test that retrieving more nearest entities than available returns all entities."""
    # Arrange
    positions = [(10, 20), (12, 22)]
    for i, position in enumerate(positions):
        wrapped_grid.add_entity(entity_ids[i], position)
    
    # Act
    result = wrapped_grid.get_nearest_entities((10, 20), 5)
    
    # Assert
    assert len(result) == 2
    assert result[0][0] == entity_ids[0]  # (10, 20)
    assert result[1][0] == entity_ids[1]  # (12, 22)


def test_get_all_entities(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that all entities can be retrieved."""
    # Arrange
    positions = [(10, 20), (30, 40), (50, 60)]
    for i, position in enumerate(positions):
        wrapped_grid.add_entity(entity_ids[i], position)
    
    # Act
    result = wrapped_grid.get_all_entities()
    
    # Assert
    assert len(result) == 3
    assert entity_ids[0] in result
    assert entity_ids[1] in result
    assert entity_ids[2] in result


def test_get_all_positions(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that all entity positions can be retrieved."""
    # Arrange
    positions = [(10, 20), (30, 40), (50, 60)]
    for i, position in enumerate(positions):
        wrapped_grid.add_entity(entity_ids[i], position)
    
    # Act
    result = wrapped_grid.get_all_positions()
    
    # Assert
    assert len(result) == 3
    assert result[entity_ids[0]] == (10, 20)
    assert result[entity_ids[1]] == (30, 40)
    assert result[entity_ids[2]] == (50, 60)


def test_clear(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that the grid can be cleared."""
    # Arrange
    positions = [(10, 20), (30, 40), (50, 60)]
    for i, position in enumerate(positions):
        wrapped_grid.add_entity(entity_ids[i], position)
    
    # Act
    wrapped_grid.clear()
    
    # Assert
    assert len(wrapped_grid) == 0
    assert len(wrapped_grid.get_all_entities()) == 0
    assert len(wrapped_grid.get_all_positions()) == 0


def test_iter(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that the grid can be iterated over."""
    # Arrange
    positions = [(10, 20), (30, 40), (50, 60)]
    for i, position in enumerate(positions):
        wrapped_grid.add_entity(entity_ids[i], position)
    
    # Act
    result = set(wrapped_grid)
    
    # Assert
    assert len(result) == 3
    assert entity_ids[0] in result
    assert entity_ids[1] in result
    assert entity_ids[2] in result


def test_len(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that the length of the grid can be retrieved."""
    # Arrange
    positions = [(10, 20), (30, 40), (50, 60)]
    for i, position in enumerate(positions):
        wrapped_grid.add_entity(entity_ids[i], position)
    
    # Act
    result = len(wrapped_grid)
    
    # Assert
    assert result == 3


def test_contains(wrapped_grid: SpatialGrid, entity_ids: List[UUID]):
    """Test that the grid can be checked for entity containment."""
    # Arrange
    entity_id = entity_ids[0]
    position: Position = (10, 20)
    wrapped_grid.add_entity(entity_id, position)
    
    # Act & Assert
    assert entity_id in wrapped_grid
    assert entity_ids[1] not in wrapped_grid 