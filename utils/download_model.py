# utils/download_model.py

import os
import requests
from tqdm import tqdm

MODELS_DIR = "models"
FACE_DETECTOR_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite"
# PERBAIKAN DI SINI: URL POSE LANDMARKER DIUBAH
POSE_LANDMARKER_MODEL_URL = "https://storage.googleapis.com/mediapipe-assets/pose_landmarker.task"

def download_file(url, dest_folder):
    """
    Downloads a file from a given URL to a specified destination folder.

    Args:
        url (str): The URL of the file to download.
        dest_folder (str): The path to the destination folder.

    Returns:
        str: The full path to the downloaded file.
    """
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    file_name = url.split('/')[-1]
    file_path = os.path.join(dest_folder, file_name)

    if os.path.exists(file_path):
        print(f"Model '{file_name}' already exists at '{file_path}'. Skipping download.")
        return file_path

    print(f"Downloading {file_name} from {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # Raise an exception for HTTP errors

        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024 # 1 Kibibyte
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

        with open(file_path, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()

        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print("ERROR, something went wrong during download.")
            raise IOError("Download incomplete.")

        print(f"Successfully downloaded '{file_name}' to '{file_path}'.")
        return file_path
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {file_name}: {e}")
        # Clean up partially downloaded file if an error occurs
        if os.path.exists(file_path):
            os.remove(file_path)
        raise

def download_model_face_detection():
    """
    Downloads the MediaPipe Face Detector model if it doesn't already exist.

    Returns:
        str: The path to the downloaded (or existing) face detector model.
    """
    return download_file(FACE_DETECTOR_MODEL_URL, MODELS_DIR)

def download_model_pose_detection():
    """
    Downloads the MediaPipe Pose Landmarker model if it doesn't already exist.

    Returns:
        str: The path to the downloaded (or existing) pose landmarker model.
    """
    return download_file(POSE_LANDMARKER_MODEL_URL, MODELS_DIR)

if __name__ == '__main__':
    # Example usage:
    try:
        face_model = download_model_face_detection()
        print(f"Face Detector Model: {face_model}")
        pose_model = download_model_pose_detection()
        print(f"Pose Landmarker Model: {pose_model}")
    except Exception as e:
        print(f"Failed to download models: {e}")