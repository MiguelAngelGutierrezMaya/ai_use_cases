#!/bin/bash

# Install main requirements
pip install -r requirements.txt

# Install problematic package without dependencies
pip install rfdetr==1.1.0 --no-deps

echo "All packages installed successfully!" 