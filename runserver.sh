#!/bin/bash

# Set PyTorch MPS fallback environment variable
export PYTORCH_ENABLE_MPS_FALLBACK=1

# Run Django server
python manage.py runserver 