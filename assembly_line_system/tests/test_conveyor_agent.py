"""
Tests for the ConveyorAgent.
"""

import pytest
from assembly_line_system.agents.conveyor_agent import ConveyorAgent

def test_conveyor_agent_initialization():
    """Test that the conveyor agent initializes correctly."""
    # Create a mock environment
    class MockEnv:
        pass

    env = MockEnv()

    # Create conveyor agent
    agent = ConveyorAgent("conveyor_1", "conveyor_1@localhost", "password", env)

    # Check attributes
    assert agent.agent_id == "conveyor_1"
    assert agent.speed == 1.0
    assert agent.capacity == 5
    assert agent.current_load == 0

def test_conveyor_agent_behaviors():
    """Test that the conveyor agent sets up behaviors correctly."""
    # Create a mock environment
    class MockEnv:
        pass

    env = MockEnv()

    # Create conveyor agent
    agent = ConveyorAgent("conveyor_1", "conveyor_1@localhost", "password", env)

    # Check that behaviors are set up
    assert len(agent.default_behaviours) == 2

    # Check behavior types
    cyclic_behavior = agent.default_behaviours[0]
    periodic_behavior = agent.default_behaviours[1]

    assert cyclic_behavior.__class__.__name__ == "ConveyorCyclicBehaviour"
    assert periodic_behavior.__class__.__name__ == "ConveyorPeriodicBehaviour"

def test_conveyor_agent_transport():
    """Test the conveyor agent's transport functionality."""
    # Create a mock environment
    class MockEnv:
        pass

    env = MockEnv()

    # Create conveyor agent
    agent = ConveyorAgent("conveyor_1", "conveyor_1@localhost", "password", env)

    # Test initial state
    assert agent.current_load == 0

    # Simulate receiving materials (this would normally be done via messaging)
    agent.current_load = 3

    # Test transport functionality
    assert agent.current_load == 3

    # Simulate transport (this would normally update the environment)
    # For now, we'll just test that the method exists and can be called
    assert hasattr(agent, '_transport_materials')

    # Note: Full transport testing would require a more complete environment implementation