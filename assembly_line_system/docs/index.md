# Assembly Line System Documentation

Welcome to the documentation for the Assembly Line System. This project implements a multi-agent assembly line simulation using SPADE for agent communication and RLlib for reinforcement learning.

## Overview

The Assembly Line System simulates an industrial assembly line where different types of agents (conveyor belts, cranes, robotic arms, and assembly stations) work together to produce finished products from raw materials. The system uses:

- **SPADE**: For multi-agent communication and coordination
- **RLlib**: For reinforcement learning algorithms
- **Gymnasium**: As the environment standard

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
- [System Overview](architecture/overview.md)
- [Agent Types](architecture/agents.md)
- [Communication Protocols](architecture/protocols.md)

### Environment
- [Design Principles](environment/design.md)
- [API Reference](environment/api.md)

### Agents
- [Base Agent](agents/base_agent.md)
- [Conveyor Agent](agents/conveyor_agent.md)

### RLlib Models
- [Model Overview](rllib/overview.md)
- [Conveyor Model](rllib/conveyor_model.md)

### Protocols
- [Material Transfer](protocols/material_transfer.md)

### Testing
- [Testing Strategy](testing/strategy.md)
- [Environment Tests](testing/env_tests.md)
- [Agent Tests](testing/agent_tests.md)

### Development
- [Project Setup](development/setup.md)
- [Contributing Guide](development/contributing.md)

## Contributing

We welcome contributions to the Assembly Line System! Please see our [contributing guide](development/contributing.md) for details on how to get involved.

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/yourusername/assembly_line_system/blob/main/LICENSE) file for details.