# utils/heart_rate.py

import numpy as np
from scipy.signal import butter, filtfilt
import cv2
import mediapipe as mp # Diperlukan untuk get_initial_roi

def cpu_POS(input_video, fps):
    """
    Estimates the rPPG signal using the Plane Orthogonal to Skin (POS) algorithm.

    Args:
        input_video (np.ndarray): A 3D numpy array of shape (1, 3, N) representing
                                  the raw r, g, b signals over time.
                                  (1, 3, N) means 1 sample, 3 channels (R, G, B), N frames/data points.
        fps (int): Frames per second of the video.

    Returns:
        np.ndarray: The extracted rPPG signal.
    """
    # Reshape input_video to (3, N)
    C = input_video[0] # Assuming input_video is (1, 3, N), take the first (and only) sample

    H = np.zeros(C.shape[1]) # Initialize output signal

    # Normalize the RGB channels
    # Menghindari pembagian oleh nol jika norm(C, axis=0) menghasilkan nol
    norm_C = C / (np.linalg.norm(C, axis=0) + 1e-6) # Add small epsilon for stability

    # Calculate alpha and beta
    alpha = np.std(norm_C[0]) / (np.std(norm_C[1]) + 1e-6)
    beta = np.std(norm_C[0]) / (np.std(norm_C[2]) + 1e-6)

    # Construct orthogonal projection plane
    S = alpha * norm_C[0] + norm_C[1]
    P = beta * norm_C[0] + norm_C[2]

    # Calculate rPPG signal (H)
    for t in range(C.shape[1]):
        H[t] = S[t] - P[t]

    return H

def bandpass_filter_signal(signal, lowcut, highcut, fs, order=5):
    """
    Applies a Butterworth bandpass filter to a signal.

    Args:
        signal (np.ndarray): The input signal to filter.
        lowcut (float): The lower cutoff frequency of the filter (Hz).
        highcut (float): The upper cutoff frequency of the filter (Hz).
        fs (int): The sampling rate of the signal (Hz).
        order (int): The order of the filter.

    Returns:
        np.ndarray: The filtered signal.
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    # Check for valid cutoff frequencies
    if low >= high:
        # If lowcut >= highcut, it's not a valid bandpass filter.
        # Return the original signal or handle as an error.
        print(f"Warning: Invalid bandpass filter parameters (lowcut={lowcut}, highcut={highcut}). Returning original signal.")
        return signal
    if not (0 < low < 1 and 0 < high < 1):
        print(f"Warning: Normalized frequencies out of range (0, 1). low={low}, high={high}. Clamping to (0.01, 0.99).")
        low = np.clip(low, 0.01, 0.99)
        high = np.clip(high, 0.01, 0.99)
        if low >= high: # Recheck after clamping
             print("Warning: Clamping resulted in invalid range. Returning original signal.")
             return signal
    try:
        b, a = butter(order, [low, high], btype='band')
        y = filtfilt(b, a, signal)
        return y
    except ValueError as e:
        print(f"Error applying bandpass filter: {e}. Returning original signal.")
        return signal


def moving_average_filter(signal, window_size):
    """
    Applies a moving average filter to a signal.

    Args:
        signal (np.ndarray): The input signal to filter.
        window_size (int): The size of the moving average window.

    Returns:
        np.ndarray: The smoothed signal.
    """
    if window_size <= 0 or len(signal) < window_size:
        # Handle cases where window_size is invalid or signal is too short
        return signal
    return np.convolve(signal, np.ones(window_size)/window_size, mode='valid')


def get_initial_roi(image, landmarker, x_size=100, y_size=30, shift_x=0, shift_y=-30):
    """
    Mengambil ROI awal dari frame webcam untuk mendeteksi sinyal respirasi
    berdasarkan pergerakan posisi bahu pasien.

    Args:
        image (np.ndarray): Frame dari webcam dalam format BGR.
        landmarker (mediapipe.tasks.vision.PoseLandmarker): Objek MediaPipe pose detector.
        x_size (int): Setengah lebar ROI pada sumbu x. Total lebar ROI adalah 2 * x_size.
        y_size (int): Setengah tinggi ROI pada sumbu y. Total tinggi ROI adalah 2 * y_size.
        shift_x (int): Pergeseran ROI pada sumbu x (nilai positif menggeser ke kanan).
        shift_y (int): Pergeseran ROI pada sumbu y (nilai positif menggeser ke bawah).

    Returns:
        tuple: Koordinat ROI (left_x, top_y, right_x, bottom_y).

    Raises:
        ValueError: Jika tidak ada pose yang terdeteksi atau dimensi ROI tidak valid.
    """
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # Mengubah warna BGR ke RGB
    height, width = image.shape[:2] # Mengambil dimensi frame webcam

    # Membuat gambar MediaPipe dari frame webcam
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=image_rgb
    )

    # Mendeteksi pose dari frame webcam
    detection_result = landmarker.detect(mp_image)

    if not detection_result.pose_landmarks:
        raise ValueError("No pose detected in frame for respiration ROI initialization! Make sure your upper body is visible.")

    # Mendeteksi tubuh pengguna dari landmark pertama
    landmarks = detection_result.pose_landmarks[0]

    # Mengambil landmark bahu kiri dan kanan (indeks 11 dan 12)
    left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]

    # Menghitung posisi tengah dari bahu kiri dan bahu kanan
    # Koordinat landmark adalah normalisasi (0-1), jadi kalikan dengan dimensi frame
    center_x = int(((left_shoulder.x + right_shoulder.x) / 2) * width)
    center_y = int(((left_shoulder.y + right_shoulder.y) / 2) * height)

    # Mengaplikasikan shift terhadap titik tengah
    center_x += shift_x
    center_y += shift_y

    # Menghitung batasan ROI berdasarkan posisi tengah dan ukuran ROI
    left_x = max(0, center_x - x_size)
    right_x = min(width, center_x + x_size)
    top_y = max(0, center_y - y_size)
    bottom_y = min(height, center_y + y_size)

    # Mevalidasi ukuran ROI
    if (right_x - left_x) <= 0 or (bottom_y - top_y) <= 0:
        raise ValueError(f"Invalid ROI dimensions: [{left_x}:{right_x}, {top_y}:{bottom_y}]. Adjust x_size, y_size, or shift parameters.")

    return (left_x, top_y, right_x, bottom_y)