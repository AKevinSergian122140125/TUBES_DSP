# main.py

import sys
import numpy as np
import cv2
import mediapipe as mp
# HAPUS BARIS INI: import mediapipe.solutions.pose as mp_pose

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import pyqtgraph as pg
from scipy.signal import find_peaks

# Import modul dari folder utils
from utils.download_model import download_model_face_detection, download_model_pose_detection
from utils.check_gpu import check_gpu
# Import fungsi-fungsi pemrosesan sinyal dari utils/heart_rate.py
from utils.heart_rate import cpu_POS, bandpass_filter_signal, moving_average_filter, get_initial_roi

# Pastikan import ini ada dan benar
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class HeartRateMonitor(QWidget):
    """
    Main Class untuk menampilkan GUI dan menghitung detak jantung dan pernapasan secara real-time.
    Kelas ini akan menyimpan nilai sinyal rppg dan nilai sinyal pernafasan dari pose detection.
    """
    def __init__(self):
        """
        Konstruktor kelas HeartRateMonitor.
        Menginisialisasi GUI, kamera, detektor MediaPipe, dan properti sinyal/plot.
        """
        super().__init__()
        self.initUI()

        # Platform Specific Camera Backend
        video_backend = cv2.CAP_DSHOW if sys.platform == 'win32' else cv2.CAP_AVFOUNDATION
        self.cap = cv2.VideoCapture(0, video_backend)
        if not self.cap.isOpened():
            print("Error: Could not open video stream. Please check webcam.")
            sys.exit(1)

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.fps == 0:
            print("Warning: FPS is 0, setting to default 30.")
            self.fps = 30

        # Properties for Storing values
        self.r_signal, self.g_signal, self.b_signal = [], [], []
        self.resp_signal = []

        # Initialize MediaPipe detectors
        self.face_detector = self.initialize_face_detector()
        self.pose_landmarker = self.initialize_pose_landmarker()

        # Inisialisasi properti untuk ROI pernapasan berbasis landmark
        self.resp_roi_center_y_history = []
        self.last_pose_landmarks = None

        self.left_x_resp = None
        self.top_y_resp = None
        self.right_x_resp = None
        self.bottom_y_resp = None
        
        # Setup QTimer for frame updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000 // int(self.fps))

    def initUI(self):
        """
        Metode untuk mempersiapkan antarmuka pengguna grafis (GUI) menggunakan PyQt5.
        Menyiapkan layout, label video, label hasil HR/RR, dan widget plot.
        """
        self.setWindowTitle('Real-Time Heart Rate and Respiration Monitor')
        self.setGeometry(100, 100, 1200, 800)

        # Prepare GUI elements
        self.video_label = QLabel(self)
        self.hr_label = QLabel('Heart Rate: -- BPM (Beat Per Minute)', self)
        self.hr_label.setAlignment(Qt.AlignCenter)
        self.resp_label = QLabel('Respiration Rate: -- BPM (Breath Per Minute)', self)
        self.resp_label.setAlignment(Qt.AlignCenter)

        # Heart Rate Plot
        self.plot_widget_hr = pg.PlotWidget()
        self.plot_widget_hr.setYRange(-3, 3)
        self.plot_widget_hr.setTitle("Heart Rate Signal (rPPG)")
        self.plot_widget_hr.setLabel('left', 'Amplitude')
        self.plot_widget_hr.setLabel('bottom', 'Samples')
        self.plot_curve_hr = self.plot_widget_hr.plot(pen='r')

        # Respiration Rate Plot
        self.plot_widget_resp = pg.PlotWidget()
        self.plot_widget_resp.setYRange(-3, 3)
        self.plot_widget_resp.setTitle("Respiration Signal")
        self.plot_widget_resp.setLabel('left', 'Amplitude')
        self.plot_widget_resp.setLabel('bottom', 'Samples')
        self.plot_curve_resp = self.plot_widget_resp.plot(pen='b')

        # Making Layout instance and insert the plot into the layout
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.hr_label)
        left_layout.addWidget(self.plot_widget_hr)
        left_layout.addWidget(self.resp_label)
        left_layout.addWidget(self.plot_widget_resp)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.video_label)

        main_layout = QGridLayout()
        main_layout.addLayout(left_layout, 0, 0)
        main_layout.addLayout(right_layout, 0, 1)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 2)

        self.setLayout(main_layout)

    def initialize_face_detector(self):
        """
        Menginisialisasi objek Face Detector dari MediaPipe untuk proses rPPG.
        Model akan diunduh jika belum ada.

        Returns:
            mediapipe.tasks.vision.FaceDetector: Objek FaceDetector yang sudah terinisialisasi.
        """
        model_path = download_model_face_detection()
        BaseOptions = mp.tasks.BaseOptions
        gpu_checked = check_gpu()
        
        if sys.platform == 'win32':
            delegate = python.BaseOptions.Delegate.CPU
        else:
            delegate = python.BaseOptions.Delegate.GPU if gpu_checked == "NVIDIA" else python.BaseOptions.Delegate.CPU
        
        options = vision.FaceDetectorOptions(
            base_options=BaseOptions(
                model_asset_path=model_path,
                delegate=delegate
            )
        )
        return vision.FaceDetector.create_from_options(options)

    def initialize_pose_landmarker(self):
        """
        Menginisialisasi objek Pose Landmarker dari MediaPipe untuk proses ekstraksi
        sinyal respirasi. Model akan diunduh jika belum ada.

        Returns:
            mediapipe.tasks.vision.PoseLandmarker: Objek PoseLandmarker yang sudah terinisialisasi.
        """
        model_path = download_model_pose_detection()
        BaseOptions = mp.tasks.BaseOptions
        PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        gpu_checked = check_gpu()

        if sys.platform == 'win32':
            delegate = BaseOptions.Delegate.CPU
        else:
            delegate = BaseOptions.Delegate.GPU if gpu_checked == "NVIDIA" else BaseOptions.Delegate.CPU
            
        options_image = PoseLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=model_path,
                delegate = delegate
            ),
            running_mode=VisionRunningMode.IMAGE,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_segmentation_masks=False
        )
        
        return mp.tasks.vision.PoseLandmarker.create_from_options(options_image)

    def update_frame(self):
        """
        Metode utama yang dipanggil secara periodik oleh QTimer untuk memproses setiap frame.
        Melakukan:
        1. Pembacaan frame dari webcam.
        2. Deteksi wajah dan ekstraksi ROI dahi untuk sinyal rPPG.
        3. Deteksi pose dan ekstraksi sinyal respirasi berbasis landmark.
        4. Pemrosesan sinyal (filtering, normalisasi, smoothing).
        5. Perhitungan detak jantung dan laju pernapasan.
        6. Pembaruan tampilan GUI (video feed, plot sinyal, label hasil).
        """
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame.")
            self.timer.stop()
            return

        h, w, _ = frame.shape

        # --- rPPG Signal Extraction (Forehead ROI) ---
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        detection_result_face = self.face_detector.detect(mp_image)

        if detection_result_face.detections:
            detection = detection_result_face.detections[0]
            bbox = detection.bounding_box
            
            # --- PENYESUAIAN KOTAK HIJAU UNTUK RPPG: KIRA-KIRA SEBESAR MUKA ---
            # Menggunakan lebar penuh wajah dan bagian atas wajah untuk ROI dahi/rPPG
            forehead_x = int(bbox.origin_x)
            forehead_y = int(bbox.origin_y)
            forehead_width = int(bbox.width)
            forehead_height = int(bbox.height * 0.4)

            forehead_x = max(0, forehead_x)
            forehead_y = max(0, forehead_y)
            forehead_width = min(forehead_width, w - forehead_x)
            forehead_height = min(forehead_height, h - forehead_y)

            if forehead_width > 0 and forehead_height > 0:
                roi_forehead = frame[forehead_y : forehead_y + forehead_height,
                                     forehead_x : forehead_x + forehead_width]
                
                if roi_forehead.size > 0:
                    self.r_signal.append(np.mean(roi_forehead[:, :, 2])) 
                    self.g_signal.append(np.mean(roi_forehead[:, :, 1]))
                    self.b_signal.append(np.mean(roi_forehead[:, :, 0]))

                    cv2.rectangle(frame, (forehead_x, forehead_y),
                                  (forehead_x + forehead_width, forehead_y + forehead_height),
                                  (0, 255, 0), 2) # Green rectangle for forehead

        # --- Respiration Signal Extraction (Landmark-based) ---
        detection_result_pose = self.pose_landmarker.detect(mp_image)

        if detection_result_pose.pose_landmarks:
            current_pose_landmarks = detection_result_pose.pose_landmarks[0]
            
            # Menggunakan indeks numerik standar untuk landmark bahu
            # LEFT_SHOULDER: 11, RIGHT_SHOULDER: 12
            left_shoulder = current_pose_landmarks[11]
            right_shoulder = current_pose_landmarks[12]
            
            # Konversi koordinat normalized (0-1) ke piksel
            shoulder_y_avg_px = int(((left_shoulder.y + right_shoulder.y) / 2) * h)
            
            # --- PENYESUAIAN SINYAL RESPIRASI: FOKUS PADA BAHU ---
            self.resp_signal.append(shoulder_y_avg_px) # Sinyal pernapasan hanya dari posisi Y bahu
            
            # --- Gambar Kotak Merah (ROI Pernapasan) yang Mengikuti ---
            # Lebar kotak berdasarkan jarak bahu
            shoulder_x_min_px = int(min(left_shoulder.x, right_shoulder.x) * w)
            shoulder_x_max_px = int(max(left_shoulder.x, right_shoulder.x) * w)
            
            box_height_resp = 20 # Tinggi kotak, dibuat lebih tipis untuk efek "garis"
            
            # Posisi Y kotak merah, berpusat pada rata-rata Y bahu
            self.top_y_resp = int(shoulder_y_avg_px - (box_height_resp / 2))
            self.bottom_y_resp = self.top_y_resp + box_height_resp

            # Lebar kotak, sedikit dilebihkan dari lebar bahu
            padding_x_resp = int((shoulder_x_max_px - shoulder_x_min_px) * 0.1) # 10% padding
            self.left_x_resp = max(0, shoulder_x_min_px - padding_x_resp)
            self.right_x_resp = min(w, shoulder_x_max_px + padding_x_resp)

            # Pastikan koordinat tetap dalam batas frame
            self.top_y_resp = max(0, self.top_y_resp)
            self.left_x_resp = max(0, self.left_x_resp)
            self.bottom_y_resp = min(h, self.bottom_y_resp)
            self.right_x_resp = min(w, self.right_x_resp)
            
            # Gambar kotak merah
            if all(v is not None for v in [self.left_x_resp, self.top_y_resp, self.right_x_resp, self.bottom_y_resp]):
                 cv2.rectangle(frame, (self.left_x_resp, self.top_y_resp), (self.right_x_resp, self.bottom_y_resp), (0, 0, 255), 2) # Merah


        # --- Signal Processing and Rate Calculation ---
        # rPPG processing
        if len(self.g_signal) >= self.fps * 10:
            rgb_signals = np.array([self.r_signal, self.g_signal, self.b_signal])
            rgb_signals_reshaped = rgb_signals.reshape(1, 3, -1) 
            
            rppg_signal_raw = cpu_POS(rgb_signals_reshaped, fps=self.fps)
            rppg_signal = rppg_signal_raw.reshape(-1)

            filtered_signal = bandpass_filter_signal(rppg_signal, 0.75, 3.0, self.fps, order=5)
            if filtered_signal.size > 0:
                normalized_signal = (filtered_signal - np.mean(filtered_signal)) / (np.std(filtered_signal) + 1e-6)
                smoothed_signal = moving_average_filter(normalized_signal, window_size=int(self.fps/2))

                if smoothed_signal.size > 0:
                    peaks_hr, _ = find_peaks(smoothed_signal, distance=self.fps / 3.0)
                    peak_intervals_hr = np.diff(peaks_hr) / self.fps
                    heart_rate = 60.0 / np.mean(peak_intervals_hr) if len(peak_intervals_hr) > 0 else 0
                else:
                    heart_rate = 0.0

                self.hr_label.setText(f'Heart Rate: {heart_rate:.2f} BPM (Beat Per Minute)')
                self.plot_curve_hr.setData(smoothed_signal)
            else:
                self.hr_label.setText(f'Heart Rate: -- BPM (Beat Per Minute)')
                self.plot_curve_hr.setData([])
            
            self.r_signal, self.g_signal, self.b_signal = [], [], []

        # Respiration processing
        if len(self.resp_signal) >= self.fps * 10:
            resp_signal_raw = np.array(self.resp_signal)
            
            filtered_resp_signal = bandpass_filter_signal(resp_signal_raw, 0.1, 0.5, self.fps, order=5)
            if filtered_resp_signal.size > 0:
                normalized_resp_signal = (filtered_resp_signal - np.mean(filtered_resp_signal)) / (np.std(filtered_resp_signal) + 1e-6)
                smoothed_resp_signal = moving_average_filter(normalized_resp_signal, window_size=int(self.fps/2))

                if smoothed_resp_signal.size > 0:
                    resp_peaks, _ = find_peaks(smoothed_resp_signal, distance=self.fps / 0.5)
                    resp_intervals = np.diff(resp_peaks) / self.fps
                    respiration_rate = 60.0 / np.mean(resp_intervals) if len(resp_intervals) > 0 else 0
                else:
                    respiration_rate = 0.0

                self.resp_label.setText(f'Respiration Rate: {respiration_rate:.2f} BPM (Breath Per Minute)')
                self.plot_curve_resp.setData(smoothed_resp_signal)
            else:
                self.resp_label.setText(f'Respiration Rate: -- BPM (Breath Per Minute)')
                self.plot_curve_resp.setData([])

            self.resp_signal = []

        # Convert frame to RGB for displaying in video_label
        frame_rgb_display = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame_rgb_display.data, frame_rgb_display.shape[1], frame_rgb_display.shape[0], QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(image.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)))

    def closeEvent(self, event):
        """
        Metode turunan dari kelas QWidget yang dipanggil ketika jendela ditutup.
        Digunakan untuk melepaskan sumber daya kamera OpenCV.

        Args:
            event (QCloseEvent): Objek event penutupan jendela.
        """
        self.cap.release()
        cv2.destroyAllWindows()
        print("Application closed, camera released.")
        event.accept()

if __name__ == '__main__':
    import os
    if not os.path.exists("models"):
        os.makedirs("models")

    app = QApplication(sys.argv)
    ex = HeartRateMonitor()
    ex.show()
    sys.exit(app.exec_())