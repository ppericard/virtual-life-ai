"""Unit tests for the Environment class."""

import pytest
from uuid import UUID, uuid4
from typing import Tuple

from virtuallife.simulation.environment import Environment


class MockEntity:
    """Mock entity class for testing."""
    def __init__(self, position: Tuple[int, int]):
        self.id = uuid4()
        self.position = position


@pytest.fixture
def env():
    """Create a test environment."""
    return Environment(width=10, height=10)


@pytest.fixture
def entity():
    """Create a test entity."""
    return MockEntity(position=(5, 5))


def test_environment_initialization():
    """Test environment initialization with different parameters."""
    env = Environment(width=10, height=20, boundary_condition="wrapped")
    assert env.width == 10
    assert env.height == 20
    assert env.boundary_condition == "wrapped"
    assert len(env.entities) == 0
    assert len(env.entity_positions) == 0
    assert len(env.resources) == 0


def test_add_entity(env, entity):
    """Test adding an entity to the environment."""
    env.add_entity(entity)
    assert entity.id in env.entities
    assert entity.id in env.entity_positions[entity.position]
    assert env.get_entities_at(entity.position) == [entity]


def test_add_duplicate_entity(env, entity):
    """Test that adding a duplicate entity raises an error."""
    env.add_entity(entity)
    with pytest.raises(ValueError):
        env.add_entity(entity)


def test_remove_entity(env, entity):
    """Test removing an entity from the environment."""
    env.add_entity(entity)
    env.remove_entity(entity.id)
    assert entity.id not in env.entities
    assert entity.position not in env.entity_positions


def test_get_entities_at(env, entity):
    """Test getting entities at a specific position."""
    env.add_entity(entity)
    entities = env.get_entities_at(entity.position)
    assert len(entities) == 1
    assert entities[0] == entity
    
    # Test empty position
    assert env.get_entities_at((0, 0)) == []


@pytest.mark.parametrize("boundary,position,expected", [
    ("wrapped", (15, 25), (5, 5)),  # 10x10 grid
    ("bounded", (15, 25), (9, 9)),  # 10x10 grid
    ("infinite", (15, 25), (15, 25)),  # No bounds
])
def test_normalize_position(env, boundary, position, expected):
    """Test position normalization for different boundary conditions."""
    env.boundary_condition = boundary
    assert env.normalize_position(position) == expected


def test_get_neighborhood(env):
    """Test getting neighborhood around a position."""
    # Add entities in a pattern
    entities = [
        MockEntity((4, 5)),  # Left
        MockEntity((6, 5)),  # Right
        MockEntity((5, 4)),  # Above
        MockEntity((5, 6)),  # Below
        MockEntity((5, 5)),  # Center
    ]
    for entity in entities:
        env.add_entity(entity)
    
    # Get neighborhood with radius 1
    neighborhood = env.get_neighborhood((5, 5), radius=1)
    
    # Should find all 5 entities
    assert len(neighborhood) == 5
    
    # Check each position has the correct entity
    for entity in entities:
        assert entity in neighborhood[entity.position]


def test_resource_management(env):
    """Test resource management functions."""
    position = (5, 5)
    
    # Test adding resource
    env.add_resource("food", position, 10.0)
    assert env.get_resource("food", position) == 10.0
    
    # Test updating resource
    env.add_resource("food", position, 20.0)
    assert env.get_resource("food", position) == 20.0
    
    # Test getting nonexistent resource
    assert env.get_resource("water", position) == 0.0
    
    # Test removing resource
    env.remove_resource("food", position)
    assert env.get_resource("food", position) == 0.0
    
    # Test removing nonexistent resource (should not raise error)
    env.remove_resource("water", position) 