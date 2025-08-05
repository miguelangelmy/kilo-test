#!/bin/bash
# Setup script for the assembly line system

echo "Setting up Assembly Line System..."

# Create virtual environment
echo "Creating virtual environment..."
python -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Pre-commit setup
echo "Setting up pre-commit hooks..."
pre-commit install

echo "Setup completed successfully!"
echo "To start the simulation, run: python -m assembly_line_system.simulation"