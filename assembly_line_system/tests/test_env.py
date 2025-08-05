"""
Tests for the AssemblyLineEnv environment.
"""

import pytest
from assembly_line_system.env.assembly_line_env import AssemblyLineEnv

def test_environment_initialization():
    """Test that the environment initializes correctly."""
    env = AssemblyLineEnv()

    # Check observation space
    assert env.observation_space.shape == (6, 3)  # 2 conveyors + 1 crane + 2 robotic arms + 1 assembly station

    # Check action space
    assert env.action_space.n == 4  # NO_OP, MOVE, PICKUP, DROP

    # Check initial observation
    obs = env.reset()
    assert obs.shape == (6, 3)

def test_environment_step():
    """Test that the environment can execute steps."""
    env = AssemblyLineEnv()

    # Reset environment
    obs = env.reset()
    assert obs.shape == (6, 3)

    # Execute a step with random actions
    actions = {
        'conveyor_1': 0,  # NO_OP
        'crane_1': 1,     # MOVE
        'robotic_arm_1': 2,  # PICKUP
        'assembly_station_1': 3   # DROP
    }

    new_obs, rewards, done, info = env.step(actions)

    # Check outputs
    assert new_obs.shape == (6, 3)
    assert isinstance(rewards, dict)
    assert isinstance(done, bool)
    assert isinstance(info, dict)

def test_environment_render():
    """Test that the environment can be rendered."""
    env = AssemblyLineEnv()
    obs = env.reset()

    # Capture output of render
    import io
    import sys

    captured_output = io.StringIO()
    sys.stdout = captured_output

    env.render()

    # Restore stdout
    sys.stdout = sys.__stdout__

    output = captured_output.getvalue()
    assert "Time step: 0" in output
    assert "Conveyors:" in output