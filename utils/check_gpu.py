# utils/check_gpu.py
import subprocess
import os

def check_gpu():
    """
    Checks for the presence of an NVIDIA GPU using nvidia-smi.

    Returns:
        str: "NVIDIA" if an NVIDIA GPU is detected, otherwise "CPU".
    """
    try:
        # Try to run nvidia-smi command
        # Capture stdout and stderr
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, check=True)
        # If the command runs without error, it means nvidia-smi is available and thus an NVIDIA GPU is likely present
        if "NVIDIA-SMI" in result.stdout:
            print("NVIDIA GPU detected.")
            return "NVIDIA"
    except (subprocess.CalledProcessError, FileNotFoundError):
        # If nvidia-smi command fails or is not found, assume no NVIDIA GPU
        print("No NVIDIA GPU detected or nvidia-smi not found. Using CPU.")
    return "CPU"

if __name__ == '__main__':
    # Example usage:
    device = check_gpu()
    print(f"Detected device: {device}")