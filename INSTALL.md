# Installation Instructions

This project has some packages with complex dependencies. Follow these steps to install all requirements:

## Option 1: Using the install script (Recommended)

```bash
./install_requirements.sh
```

## Option 2: Manual installation

1. Install main packages from requirements.txt:
```bash
pip install -r requirements.txt
```

2. Install rfdetr without its dependencies:
```bash
pip install rfdetr==1.1.0 --no-deps
```

## Troubleshooting

- **Module not found errors**: If you encounter errors like `ModuleNotFoundError: No module named 'torchvision'`, make sure to install the missing package:
  ```bash
  pip install torchvision>=0.22.0
  ```

- **CMake errors**: If you encounter CMake-related errors, make sure you have cmake installed on your system:
  ```bash
  brew install cmake  # On macOS with Homebrew
  ```

- **onnxsim errors**: The rfdetr package depends on onnxsim which can be problematic to install. The `--no-deps` flag helps avoid this issue.

- **Missing functionality**: Installing rfdetr without dependencies might limit some functionality. If you need specific features, you may need to manually install additional dependencies. 