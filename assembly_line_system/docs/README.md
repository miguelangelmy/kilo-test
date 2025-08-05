# Assembly Line System Documentation

Welcome to the documentation for the Assembly Line System. This project implements a multi-agent assembly line simulation using SPADE for agent communication and RLlib for reinforcement learning.

## Table of Contents

### Architecture
- [Overview](architecture/overview.md)
- [Agents](architecture/agents.md)
- [Protocols](architecture/protocols.md)

### Environment
- [Design](environment/design.md)
- [API Reference](environment/api.md)

### Agents
- [Base Agent](agents/base_agent.md)
- [Conveyor Agent](agents/conveyor_agent.md)

### RLlib Models
- [Overview](rllib/overview.md)
- [Conveyor Model](rllib/conveyor_model.md)

### Protocols
- [Material Transfer](protocols/material_transfer.md)

### Testing
- [Strategy](testing/strategy.md)
- [Environment Tests](testing/env_tests.md)
- [Agent Tests](testing/agent_tests.md)

### Development
- [Setup](development/setup.md)
- [Contributing](development/contributing.md)

## Getting Started

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/assembly_line_system.git

# Navigate to the project directory
cd assembly_line_system

# Install dependencies
pip install -r requirements.txt

# Set up the project
./setup.sh
```

### Running the Simulation
```bash
# Run a basic simulation
python -m assembly_line_system.simulation
```

### Training Agents
```bash
# Train a conveyor belt agent
python -m assembly_line_system.rllib_models.train_conveyor
```

## Key Components

### Architecture
The system architecture consists of:
- **Environment**: Gymnasium-based simulation
- **Agents**: SPADE agents representing assembly line components
- **Protocols**: Standardized communication between agents
- **RLlib Models**: Reinforcement learning for agent decision making

### Agents
Different types of agents work together:
- **Conveyor Belt Agents**: Transport materials between stations
- **Crane Agents**: Move heavy objects between areas
- **Robotic Arm Agents**: Perform precise assembly tasks
- **Assembly Station Agents**: Assemble final products

### Protocols
Standardized protocols enable reliable communication:
- **Material Transfer**: Coordinate material movement
- **Task Assignment**: Dynamically allocate tasks
- **Status Update**: Maintain situational awareness
- **Emergency**: Handle unexpected events

### RLlib Models
Agents learn optimal behaviors through:
- **Policy Networks**: Determine agent actions
- **Value Networks**: Evaluate state values
- **Experience Replay**: Store learning experiences

## Development Workflow

1. **Fork the Repository**
2. **Create a Feature Branch**: `git checkout -b feature/your-feature-name`
3. **Make Changes**
4. **Run Tests**: `pytest`
5. **Run Pre-commit Hooks**: `pre-commit run --all-files`
6. **Push Changes**: `git push origin feature/your-feature-name`
7. **Create Pull Request**

## Contributing

We welcome contributions! Please see our [contributing guide](development/contributing.md) for details on how to get involved.

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/yourusername/assembly_line_system/blob/main/LICENSE) file for details.

## Acknowledgments

- SPADE team for the multi-agent framework
- Ray/Rllib team for the reinforcement learning library
- Gymnasium team for the RL environment standard

This documentation provides comprehensive information about the Assembly Line System, enabling developers to understand and contribute to the project effectively.