#!/bin/bash
# Setup script for Animation Laboratory Works

echo "Setting up virtual environment..."

# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -q -r requirements.txt

echo "✓ Virtual environment created and dependencies installed"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate  (on macOS/Linux)"
echo "  venv\\Scripts\\activate     (on Windows)"
echo ""
echo "Then run:"
echo "  python main.py 1  (for Lab 1: Lorenz Attractor)"
echo "  python main.py 2  (for Lab 2: Newton Fractal)"
