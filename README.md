# Assembly Line System

## Overview
This project implements a multi-agent assembly line system using SPADE for agent communication and RLlib for reinforcement learning. The system simulates an industrial assembly line with conveyor belts, cranes, robotic arms, and assembly stations working together to produce finished products from raw materials.

## Features
- **Gymnasium-compatible environment**: Standardized reinforcement learning interface
- **SPADE-based agents**: Multi-agent communication using XMPP protocols
- **RLlib integration**: Reinforcement learning for agent optimization
- **Modular design**: Easy extension with new agent types and components

## Project Structure

```
assembly_line_system/
├── agents/                # Agent implementations
│   ├── base_agent.py      # Base agent class
│   └── conveyor_agent.py  # Conveyor belt agent
├── env/                  # Environment implementations
│   └── assembly_line_env.py  # Gymnasium environment
├── protocols/            # Communication protocols
│   └── material_transfer.py  # Material transfer protocol
├── rllib_models/         # RLlib model implementations
│   ├── conveyor_model.py  # Conveyor belt model
│   └── train_conveyor.py  # Training script
├── simulation/           # Simulation scripts
│   └── __main__.py       # Main simulation entry point
├── tests/                # Test suite
│   ├── test_env.py       # Environment tests
│   ├── test_conveyor_agent.py  # Conveyor agent tests
│   ├── test_protocols.py  # Protocol tests
│   └── test_rllib_models.py  # RLlib model tests
├── requirements.txt      # Project dependencies
└── setup.py              # Package configuration
```

## Getting Started

### Prerequisites
- Python 3.8+
- pip for package installation

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
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

## Architecture

### System Components
1. **Environment**: Gymnasium-based simulation of the assembly line
2. **Agents**: SPADE agents representing different components (conveyors, cranes, etc.)
3. **Protocols**: Standardized communication between agents
4. **RLlib Models**: Reinforcement learning models for agent decision making

### Agent Types
- **Conveyor Belt Agents**: Transport materials between stations
- **Crane Agents**: Move heavy objects between areas
- **Robotic Arm Agents**: Perform precise assembly tasks
- **Assembly Station Agents**: Assemble final products

## Communication Protocols

### Material Transfer Protocol
- **REQUEST_TRANSFER**: Source agent requests material transfer
- **CONFIRM_TRANSFER**: Target agent confirms readiness
- **EXECUTE_TRANSFER**: Source agent initiates transfer
- **TRANSFER_COMPLETE**: Target agent confirms completion

### Other Protocols
- Task assignment
- Status updates
- Emergency handling

## Reinforcement Learning

### Training Approach
- **On-policy learning**: Agents learn while actively participating
- **Curriculum learning**: Start with simple tasks, gradually increase complexity
- **Shared experience pool**: Agents share successful strategies

### Model Architecture
- Shared base model with common layers
- Agent-specific policy networks
- Value networks for state evaluation

## Testing

### Test Coverage
- Environment functionality
- Agent behavior
- Communication protocols
- RLlib model training

### Running Tests
```bash
# Run all tests
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- SPADE team for the multi-agent framework
- Ray/Rllib team for the reinforcement learning library
- Gymnasium team for the RL environment standard