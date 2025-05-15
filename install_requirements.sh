#!/bin/bash

# Install main requirements
pip install -r requirements.txt

# Install problematic package without dependencies
pip install rfdetr==1.1.0 --no-deps
pip install rfdetr[metrics] --no-deps
pip install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu


echo "All packages installed successfully!" 