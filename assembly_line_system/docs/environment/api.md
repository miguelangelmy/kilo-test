# Environment API Reference

## Overview
The Assembly Line System environment follows the Gymnasium standard for reinforcement learning environments. This document provides a comprehensive reference for the environment API.

## Environment Class

### AssemblyLineEnv
The main environment class that simulates the assembly line.

#### Initialization
```python
from assembly_line_system.env.assembly_line_env import AssemblyLineEnv

env = AssemblyLineEnv(num_conveyors=2, num_cranes=1, num_robotic_arms=2, num_assembly_stations=2)
```

#### Parameters
- `num_conveyors` (int): Number of conveyor belts in the environment (default: 2)
- `num_cranes` (int): Number of cranes in the environment (default: 1)
- `num_robotic_arms` (int): Number of robotic arms in the environment (default: 2)
- `num_assembly_stations` (int): Number of assembly stations in the environment (default: 2)

## Environment Interface

### reset()
```python
observation = env.reset()
```

**Returns:**
- `observation` (numpy.ndarray): Initial observation of the environment

**Description:**
Resets the environment to its initial state and returns an initial observation.

### step(actions)
```python
observation, reward, done, info = env.step(actions)
```

**Parameters:**
- `actions` (dict): Dictionary mapping agent IDs to actions

**Returns:**
- `observation` (numpy.ndarray): New state of the environment
- `reward` (dict): Reward signal for each agent
- `done` (bool): Whether the episode has ended
- `info` (dict): Additional information

**Description:**
Executes one time step in the environment with the given actions.

### render(mode='human')
```python
env.render(mode='human')
```

**Parameters:**
- `mode` (str): Rendering mode ('human', 'ansi') (default: 'human')

**Description:**
Renders the environment to the console.

## Observation Space

The observation space is a 2D array with shape `(total_stations, 3)` where `total_stations` is the sum of all stations (conveyors + cranes + robotic arms + assembly stations).

### Observation Structure
Each row represents a station and contains:
1. **Station Type** (float): Encoded as 0-3
   - 0: Conveyor Belt
   - 1: Crane
   - 2: Robotic Arm
   - 3: Assembly Station

2. **Occupancy** (float): Normalized value between 0 and 1 representing the station's current load

3. **Queue Length** (float): Normalized value between 0 and 1 representing the number of materials waiting at the station

## Action Space

The action space is discrete with 4 possible actions for each agent:

### Action Codes
- `0`: NO_OP - No operation (agent does nothing)
- `1`: MOVE - Move materials between stations
- `2`: PICKUP - Pick up materials from a station
- `3`: DROP - Drop materials at a station

## Reward Structure

The reward signal is calculated based on the agent's performance and consists of:

1. **Task Completion Rewards**: Positive rewards for successfully completing tasks
2. **Efficiency Penalties**: Negative rewards for inefficient operations (e.g., delays, jams)
3. **Safety Bonuses**: Additional rewards for safe operations
4. **Quality Rewards**: Bonuses for maintaining product quality

## Terminal Conditions

The environment episode ends when any of the following conditions are met:

1. **Maximum Time Steps**: The simulation reaches 1000 time steps (temporary limit)
2. **Production Targets**: A predefined number of products are assembled
3. **Critical Failures**: Multiple critical failures occur in the system

## Internal Methods

### _execute_action(agent_id, action)
```python
env._execute_action(agent_id, action)
```

**Parameters:**
- `agent_id` (str): ID of the agent executing the action
- `action` (int): Action code

**Description:**
Executes a specific agent's action in the environment.

### _update_materials()
```python
env._update_materials()
```

**Description:**
Updates the state of materials in the environment, moving them through the system.

### _check_terminal_conditions()
```python
done = env._check_terminal_conditions()
```

**Returns:**
- `done` (bool): Whether terminal conditions are met

**Description:**
Checks if any terminal conditions have been reached.

### _calculate_reward()
```python
reward = env._calculate_reward()
```

**Returns:**
- `reward` (dict): Reward signal for each agent

**Description:**
Calculates the reward signal based on current performance.

### _get_observation()
```python
observation = env._get_observation()
```

**Returns:**
- `observation` (numpy.ndarray): Current observation of the environment

**Description:**
Generates the current observation vector for all agents.

## Example Usage

```python
# Create environment
env = AssemblyLineEnv()

# Reset environment
observation = env.reset()
print("Initial observation:", observation)

# Run for a few time steps
for step in range(5):
    print(f"\n--- Time Step {step} ---")

    # Take random actions for demonstration
    actions = {
        'conveyor_1': env.action_space.sample(),
        'crane_1': env.action_space.sample(),
        'robotic_arm_1': env.action_space.sample(),
        'assembly_station_1': env.action_space.sample()
    }

    # Execute actions
    observation, rewards, done, info = env.step(actions)

    print(f"Actions: {actions}")
    print(f"Rewards: {rewards}")
    print(f"Done: {done}")

    # Render environment
    env.render()

    if done:
        print("Simulation completed!")
        break
```

This API reference provides a comprehensive overview of the Assembly Line System environment, enabling developers to understand and interact with the simulation effectively.