import os
import torch
from rfdetr import RFDETRBase

# Paths
DATASET_PATH = "train_datasets/plates"
OUTPUT_PATH = "train_outputs/plates"

# Create the output directory
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Set environment variable for MPS fallback
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# Determine the device to use
device = 'cpu'

if torch.cuda.is_available():
    device = 'cuda'
elif hasattr(torch, 'backends') and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    device = 'mps'  # Use Metal Performance Shaders for Apple Silicon

# Initialize the model
model = RFDETRBase(pretrain_weights="../rf-detr-base.pth")

print(f"Configuring training parameters for device: {device}")
try:
    model.train(
        dataset_dir=DATASET_PATH,
        epochs=15,  # Adjust this value! Start with a few epochs (e.g., 10-20) and increase if necessary.
        batch_size=4,  # Recommended for T4
        grad_accum_steps=4,  # Recommended for T4 (total batch size = 16)
        lr=1e-4,
        output_dir=OUTPUT_PATH,
        checkpoint_interval=5, # Save a checkpoint every 5 epochs
        device=device, # Use the detected device
        # --- Optional: Enable Early Stopping ---
        early_stopping=True,
        early_stopping_patience=5, # Number of epochs without improvement before stopping
        early_stopping_min_delta=0.005, # Minimum improvement in mAP to reset the counter
        # --- Optional: Enable Logging ---
        tensorboard=True, # Save logs for TensorBoard
        # wandb=True, project="mi_proyecto_rfdetr", run="run_inicial" # Save logs in Weights & Biases (requires login: !wandb login)
    )
    print("\n--- Fine-Tuning completed ---")
    print(f"The checkpoints are located in: {OUTPUT_PATH}")
    # During training, two checkpoints are saved: 'checkpoint.pth' and 'checkpoint_ema.pth'.
    # The EMA (Exponential Moving Average) usually gives better results. [Source 38]
except Exception as e:
    print(f"\n--- ERROR during training ---")
    print(e)
    print("Possible causes:")
    print("- Ensure the dataset path is correct and the COCO format is valid.")
    print("- Check that you have enough disk space.")
    print("- If you use W&B, ensure you have logged in.")
    print("- If using Apple Silicon (M1/M2/M3), some operations may not be supported by MPS.")