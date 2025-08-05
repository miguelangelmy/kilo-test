# Project Setup Guide

## Overview
This guide provides step-by-step instructions for setting up the Assembly Line System development environment.

## Prerequisites

- Python 3.8+
- Git
- Basic knowledge of virtual environments

## Setup Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/assembly_line_system.git
cd assembly_line_system
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.\.venv\Scripts\Activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Up Pre-commit Hooks

```bash
pre-commit install
```

### 6. Verify Installation

```bash
python -c "import spade; import ray; import gymnasium; print('Dependencies installed successfully')"
```

## Development Workflow

### 1. Start Working on a Feature

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes and Commit

```bash
# Make your changes
git add .
git commit -m "Add your feature"
```

### 3. Run Pre-commit Hooks

```bash
pre-commit run --all-files
```

### 4. Push Your Changes

```bash
git push origin feature/your-feature-name
```

### 5. Create a Pull Request

Go to the GitHub repository and create a pull request from your feature branch.

## Running the System

### Start Simulation

```bash
python -m assembly_line_system.simulation
```

### Train Agents

```bash
python -m assembly_line_system.rllib_models.train_conveyor
```

### Run Tests

```bash
pytest
```

## Building Documentation

```bash
mkdocs build
```

## Troubleshooting

### Common Issues

1. **Virtual Environment Not Activated**:
   - Ensure you've activated the virtual environment
   - Check that your prompt shows `(venv)` or equivalent

2. **Missing Dependencies**:
   - Run `pip install -r requirements.txt` again
   - Check that you're in the correct directory

3. **SPADE Connection Issues**:
   - Ensure XMPP server is running
   - Check network connectivity

4. **RLlib Training Errors**:
   - Verify GPU availability if using CUDA
   - Check Ray cluster configuration

## Best Practices

1. **Use Virtual Environments**: Always work within the project's virtual environment
2. **Run Pre-commit Hooks**: Before committing, run `pre-commit run --all-files`
3. **Write Tests**: Add tests for new functionality
4. **Document Changes**: Update documentation when making significant changes
5. **Keep Branches Updated**: Regularly merge from main to keep branches up-to-date

This setup guide should help you get started with developing the Assembly Line System. If you encounter any issues or have questions, please check the [contributing guide](contributing.md) or open an issue on GitHub.