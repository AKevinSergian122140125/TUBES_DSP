# Real-Time Heart Rate and Respiration Monitor (IF3024 Final Project 2025)

## Deskripsi Proyek

Proyek ini adalah aplikasi *real-time* berbasis Python yang memanfaatkan kamera webcam untuk mengukur detak jantung (Heart Rate/HR) dan laju pernapasan (Respiration Rate/RR) seseorang. Pengukuran ini dilakukan melalui analisis visual:
* **Detak Jantung (rPPG):** Diekstraksi dari perubahan warna kulit wajah (remote-photoplethysmography) di area dahi.
* **Laju Pernapasan:** Diekstraksi dari pergerakan vertikal bahu menggunakan deteksi *pose landmark* dari MediaPipe.

Program ini dirancang untuk memproses video secara *real-time*, menampilkan *live feed* dari kamera dengan indikator ROI (Region of Interest), serta memvisualisasikan sinyal detak jantung dan pernapasan dalam grafik dinamis menggunakan Pyqtgraph. Hasil perhitungan HR dan RR dalam BPM (Beats/Breaths Per Minute) juga ditampilkan secara langsung.

Program ini mengimplementasikan filter digital untuk membersihkan sinyal dan algoritma deteksi puncak untuk menghitung laju fisiologis secara akurat.

## Anggota Kelompok

* **Nama Lengkap:** [A KEVIN SERGIAN]
    * **NIM:** [122140125]
    * **GitHub ID:** [@AKevinSergian122140125](https://github.com/AKevinSergian122140125)


## Logbook Mingguan Proyek

Berikut adalah catatan progres dan pembaruan proyek setiap minggunya, yang mencerminkan tantangan dan solusi yang diterapkan:

**Minggu 1: [Tanggal Awal Minggu, cth: 20 Mei 2025] - [Tanggal Akhir Minggu, cth: 26 Mei 2025]**
* Inisialisasi repositori GitHub dan struktur proyek dasar (folder `utils/`, `models/`).
* Pembuatan file `requirements.txt` awal.
* Setup lingkungan pengembangan dan instalasi dependensi via `pip install -r requirements.txt`.
    * **Tantangan:** `pip install` mengalami kendala dan hanya menginstal sebagian paket (`requests`, `tqdm`). Peringatan versi `pip` lama terus muncul.
    * **Solusi:** Diagnosa masalah instalasi. `pip --version` mengonfirmasi `pip` versi lama. Upgrade `pip` secara manual (`python -m pip install --upgrade pip` atau `& "python.exe" -m pip install --upgrade pip` di PowerShell) akhirnya berhasil.
* Integrasi dasar OpenCV dan MediaPipe ke `main.py` untuk *live feed* webcam dan deteksi wajah.

**Minggu 2: [Tanggal Awal Minggu, cth: 27 Mei 2025] - [Tanggal Akhir Minggu, cth: 2 Juni 2025]**
* Implementasi GUI dasar menggunakan PyQt5 dan Pyqtgraph untuk plot dummy.
* **Tantangan:** `ModuleNotFoundError` untuk paket-paket inti (`numpy`, `opencv-python`, dll.) meskipun `requirements.txt` sudah dijalankan.
    * **Solusi:** Ditemukan bahwa paket-paket tersebut belum terinstal di `venv`. Dilakukan instalasi paket-paket besar secara terpisah (`pip install numpy`, `pip install opencv-python`, `pip install mediapipe`, `pip install PyQt5`, `pip install pyqtgraph`, `pip install scipy`, `pip install requests`, `pip install tqdm`).
* **Tantangan:** `NameError: name 'python' is not defined` saat inisialisasi MediaPipe Face Detector.
    * **Solusi:** Baris `from mediapipe.tasks import python` yang penting hilang dari `main.py`, kemudian dikembalikan.
* **Tantangan:** `ImportError: cannot import name 'vision' from 'mediapipe.tasks'`.
    * **Solusi:** Jalur import `vision` diperbaiki menjadi `from mediapipe.tasks.python import vision`.
* **Tantangan:** `NotImplementedError: GPU Delegate is not yet supported for Windows` dari MediaPipe.
    * **Solusi:** Logika inisialisasi MediaPipe delegate diubah di `main.py` agar selalu menggunakan `CPU delegate` ketika sistem operasi adalah Windows (`if sys.platform == 'win32':`).
* **Tantangan:** `requests.exceptions.HTTPError: 404 Client Error: Not Found` saat mengunduh model `pose_landmarker_full.task`.
    * **Solusi:** URL model `POSE_LANDMARKER_MODEL_URL` di `utils/download_model.py` diperbarui ke `https://storage.googleapis.com/mediapipe-assets/pose_landmarker.task` karena model sebelumnya tidak ada di Google Storage.
* **Tantangan:** `ModuleNotFoundError: No module named 'mediapipe.solutions'` setelah beralih ke `pose_landmarker.task`.
    * **Solusi:** Referensi `mp_pose.PoseLandmark.XYZ.value` di `main.py` (yang berasal dari modul `mediapipe.solutions.pose` yang lama) diganti dengan indeks numerik standar (11, 12, 23, 24) untuk *landmark* pose.

**Minggu 3: [Tanggal Awal Minggu, cth: 3 Juni 2025] - [Tanggal Akhir Minggu, cth: 9 Juni 2025]**
* Implementasi logika ekstraksi sinyal rPPG:
    * Ekstraksi ROI dahi dan pengumpulan sinyal RGB.
    * Penerapan algoritma `cpu_POS`.
    * **Penyesuaian visual kotak hijau (ROI rPPG)** agar kira-kira sebesar wajah bagian atas (lebar penuh wajah, tinggi 40% dari wajah).
* Implementasi logika ekstraksi sinyal pernapasan:
    * Beralih dari *optical flow* ke pelacakan berbasis *pose landmark* MediaPipe untuk stabilitas yang lebih baik.
    * **Penyesuaian visual kotak merah (ROI Respirasi)** agar fokus pada bahu dan tampak seperti garis tipis yang mengikuti pergerakan bahu.
* Integrasi filter (`bandpass_filter_signal`, `moving_average_filter`) dan perhitungan laju (HR/RR) ke `main.py`.
* **Kalibrasi Awal Sinyal Pernapasan:** Penyesuaian parameter filter pernapasan berdasarkan pengukuran manual (contoh: 12 BPM).
* **Kalibrasi Awal Sinyal Detak Jantung:** Penyesuaian parameter filter rPPG berdasarkan pengukuran manual (contoh: 72 BPM).

**Minggu 4: [Tanggal Awal Minggu, cth: 10 Juni 2025] - [Tanggal Akhir Minggu, cth: 16 Juni 2025]**
* [Lanjutkan mencatat progres Anda di sini. Ini mungkin termasuk:]
    * Tuning parameter filter secara lebih mendalam untuk mendapatkan kualitas sinyal terbaik.
    * Pengujian di berbagai kondisi pencahayaan.
    * Menganalisis performa *real-time*.
    * Memastikan kelengkapan *docstring* dan komentar kode.
    * Mulai menulis laporan teknis (`report.pdf`).



## Struktur Proyek

├── models/                 # Direktori untuk menyimpan model MediaPipe yang diunduh secara otomatis
│   ├── blaze_face_short_range.tflite
│   └── pose_landmarker.task
├── utils/                  # Direktori untuk modul-modul pendukung
│   ├── check_gpu.py        # Modul untuk memeriksa ketersediaan GPU
│   ├── download_model.py   # Modul untuk mengunduh model eksternal
│   └── heart_rate.py       # Modul berisi algoritma rPPG (cpu_POS), filter, dan fungsi ROI pernapasan
├── main.py                 # File utama aplikasi (GUI, logika utama)
├── requirements.txt        # Daftar dependensi Python
├── README.md               # Dokumentasi proyek ini
├── report.pdf              # Laporan teknis proyek 
└── LICENSE                 

## Instruksi Instalasi

Untuk menjalankan program ini, ikuti langkah-langkah berikut:

1.  **Clone repositori:**
    Buka terminal atau Command Prompt, navigasi ke direktori tempat Anda ingin menyimpan proyek, lalu jalankan:
    ```bash
    git clone [URL_REPO_GITHUB_ANDA]
    cd [NAMA_FOLDER_PROYEK_ANDA]
    ```
    (Ganti `[URL_REPO_GITHUB_ANDA]` dengan URL repositori Anda dan `[NAMA_FOLDER_PROYEK_ANDA]` dengan nama folder yang dibuat oleh Git).

2.  **Buat dan aktifkan virtual environment (sangat disarankan):**
    ```bash
    python -m venv venv
    # Di Windows:
    venv\Scripts\activate
    # Di macOS/Linux:
    source venv/bin/activate
    ```

3.  **Upgrade `pip` (Penting!):**
    Untuk menghindari masalah instalasi, pastikan `pip` Anda adalah versi terbaru. Saat `venv` aktif, jalankan:
    * Di Windows (PowerShell):
        ```bash
        & ".\venv\Scripts\python.exe" -m pip install --upgrade pip
        ```
    * Di Windows (Command Prompt) / macOS / Linux:
        ```bash
        python -m pip install --upgrade pip
        ```

4.  **Instal semua dependensi:**
    ```bash
    pip install -r requirements.txt
    ```
    Model MediaPipe (`.tflite` atau `.task` files) akan diunduh secara otomatis ke direktori `models/` saat program pertama kali dijalankan (membutuhkan koneksi internet).

## Penggunaan Program

Setelah instalasi selesai, Anda dapat menjalankan program dengan perintah berikut:

```bash
python main.py

Tentu, mari kita siapkan file README.md Anda. Ini adalah salah satu bagian terpenting untuk dokumentasi proyek Anda di GitHub.

Kita akan mengisi setiap bagian README.md sesuai dengan ketentuan rubrik, terutama Logbook Mingguan yang sangat penting untuk menunjukkan progres Anda.

Berikut adalah kerangka README.md yang lengkap. Anda perlu mengisi bagian-bagian dalam kurung siku [ ] dengan informasi spesifik proyek Anda.

Markdown

# Real-Time Heart Rate and Respiration Monitor (IF3024 Final Project 2025)

## Deskripsi Proyek

Proyek ini adalah aplikasi *real-time* berbasis Python yang memanfaatkan kamera webcam untuk mengukur detak jantung (Heart Rate/HR) dan laju pernapasan (Respiration Rate/RR) seseorang. Pengukuran ini dilakukan melalui analisis visual:
* **Detak Jantung (rPPG):** Diekstraksi dari perubahan warna kulit wajah (remote-photoplethysmography) di area dahi.
* **Laju Pernapasan:** Diekstraksi dari pergerakan vertikal bahu menggunakan deteksi *pose landmark* dari MediaPipe.

Program ini dirancang untuk memproses video secara *real-time*, menampilkan *live feed* dari kamera dengan indikator ROI (Region of Interest), serta memvisualisasikan sinyal detak jantung dan pernapasan dalam grafik dinamis menggunakan Pyqtgraph. Hasil perhitungan HR dan RR dalam BPM (Beats/Breaths Per Minute) juga ditampilkan secara langsung.

Program ini mengimplementasikan filter digital untuk membersihkan sinyal dan algoritma deteksi puncak untuk menghitung laju fisiologis secara akurat.

## Anggota Kelompok

* **Nama Lengkap:** [NAMA LENGKAP ANDA]
    * **NIM:** [NIM ANDA]
    * **GitHub ID:** [@username_github_anda](https://github.com/username_github_anda)
* [Jika ada anggota lain, tambahkan di sini:]
* **Nama Lengkap:** [NAMA LENGKAP ANGGOTA 2]
    * **NIM:** [NIM ANGGOTA 2]
    * **GitHub ID:** [@username_github_anggota_2](https://github.com/username_github_anggota_2)

## Logbook Mingguan Proyek

Berikut adalah catatan progres dan pembaruan proyek setiap minggunya, yang mencerminkan tantangan dan solusi yang diterapkan:

**Minggu 1: [Tanggal Awal Minggu, cth: 20 Mei 2025] - [Tanggal Akhir Minggu, cth: 26 Mei 2025]**
* Inisialisasi repositori GitHub dan struktur proyek dasar (folder `utils/`, `models/`).
* Pembuatan file `requirements.txt` awal.
* Setup lingkungan pengembangan dan instalasi dependensi via `pip install -r requirements.txt`.
    * **Tantangan:** `pip install` mengalami kendala dan hanya menginstal sebagian paket (`requests`, `tqdm`). Peringatan versi `pip` lama terus muncul.
    * **Solusi:** Diagnosa masalah instalasi. `pip --version` mengonfirmasi `pip` versi lama. Upgrade `pip` secara manual (`python -m pip install --upgrade pip` atau `& "python.exe" -m pip install --upgrade pip` di PowerShell) akhirnya berhasil.
* Integrasi dasar OpenCV dan MediaPipe ke `main.py` untuk *live feed* webcam dan deteksi wajah.

**Minggu 2: [Tanggal Awal Minggu, cth: 27 Mei 2025] - [Tanggal Akhir Minggu, cth: 2 Juni 2025]**
* Implementasi GUI dasar menggunakan PyQt5 dan Pyqtgraph untuk plot dummy.
* **Tantangan:** `ModuleNotFoundError` untuk paket-paket inti (`numpy`, `opencv-python`, dll.) meskipun `requirements.txt` sudah dijalankan.
    * **Solusi:** Ditemukan bahwa paket-paket tersebut belum terinstal di `venv`. Dilakukan instalasi paket-paket besar secara terpisah (`pip install numpy`, `pip install opencv-python`, `pip install mediapipe`, `pip install PyQt5`, `pip install pyqtgraph`, `pip install scipy`, `pip install requests`, `pip install tqdm`).
* **Tantangan:** `NameError: name 'python' is not defined` saat inisialisasi MediaPipe Face Detector.
    * **Solusi:** Baris `from mediapipe.tasks import python` yang penting hilang dari `main.py`, kemudian dikembalikan.
* **Tantangan:** `ImportError: cannot import name 'vision' from 'mediapipe.tasks'`.
    * **Solusi:** Jalur import `vision` diperbaiki menjadi `from mediapipe.tasks.python import vision`.
* **Tantangan:** `NotImplementedError: GPU Delegate is not yet supported for Windows` dari MediaPipe.
    * **Solusi:** Logika inisialisasi MediaPipe delegate diubah di `main.py` agar selalu menggunakan `CPU delegate` ketika sistem operasi adalah Windows (`if sys.platform == 'win32':`).
* **Tantangan:** `requests.exceptions.HTTPError: 404 Client Error: Not Found` saat mengunduh model `pose_landmarker_full.task`.
    * **Solusi:** URL model `POSE_LANDMARKER_MODEL_URL` di `utils/download_model.py` diperbarui ke `https://storage.googleapis.com/mediapipe-assets/pose_landmarker.task` karena model sebelumnya tidak ada di Google Storage.
* **Tantangan:** `ModuleNotFoundError: No module named 'mediapipe.solutions'` setelah beralih ke `pose_landmarker.task`.
    * **Solusi:** Referensi `mp_pose.PoseLandmark.XYZ.value` di `main.py` (yang berasal dari modul `mediapipe.solutions.pose` yang lama) diganti dengan indeks numerik standar (11, 12, 23, 24) untuk *landmark* pose.

**Minggu 3: [Tanggal Awal Minggu, cth: 3 Juni 2025] - [Tanggal Akhir Minggu, cth: 9 Juni 2025]**
* Implementasi logika ekstraksi sinyal rPPG:
    * Ekstraksi ROI dahi dan pengumpulan sinyal RGB.
    * Penerapan algoritma `cpu_POS`.
    * **Penyesuaian visual kotak hijau (ROI rPPG)** agar kira-kira sebesar wajah bagian atas (lebar penuh wajah, tinggi 40% dari wajah).
* Implementasi logika ekstraksi sinyal pernapasan:
    * Beralih dari *optical flow* ke pelacakan berbasis *pose landmark* MediaPipe untuk stabilitas yang lebih baik.
    * **Penyesuaian visual kotak merah (ROI Respirasi)** agar fokus pada bahu dan tampak seperti garis tipis yang mengikuti pergerakan bahu.
* Integrasi filter (`bandpass_filter_signal`, `moving_average_filter`) dan perhitungan laju (HR/RR) ke `main.py`.
* **Kalibrasi Awal Sinyal Pernapasan:** Penyesuaian parameter filter pernapasan berdasarkan pengukuran manual (contoh: 12 BPM).
* **Kalibrasi Awal Sinyal Detak Jantung:** Penyesuaian parameter filter rPPG berdasarkan pengukuran manual (contoh: 72 BPM).

**Minggu 4: [Tanggal Awal Minggu, cth: 10 Juni 2025] - [Tanggal Akhir Minggu, cth: 16 Juni 2025]**
* [Lanjutkan mencatat progres Anda di sini. Ini mungkin termasuk:]
    * Tuning parameter filter secara lebih mendalam untuk mendapatkan kualitas sinyal terbaik.
    * Pengujian di berbagai kondisi pencahayaan.
    * Menganalisis performa *real-time*.
    * Memastikan kelengkapan *docstring* dan komentar kode.
    * Mulai menulis laporan teknis (`report.pdf`).

**(Lanjutkan logbook ini setiap minggu sesuai progres aktual Anda hingga proyek selesai)**

## Struktur Proyek

.
├── models/                 # Direktori untuk menyimpan model MediaPipe yang diunduh secara otomatis
│   ├── blaze_face_short_range.tflite
│   └── pose_landmarker.task
├── utils/                  # Direktori untuk modul-modul pendukung
│   ├── check_gpu.py        # Modul untuk memeriksa ketersediaan GPU
│   ├── download_model.py   # Modul untuk mengunduh model eksternal
│   └── heart_rate.py       # Modul berisi algoritma rPPG (cpu_POS), filter, dan fungsi ROI pernapasan
├── main.py                 # File utama aplikasi (GUI, logika utama)
├── requirements.txt        # Daftar dependensi Python
├── README.md               # Dokumentasi proyek ini
├── report.pdf              # Laporan teknis proyek (akan Anda buat)
└── LICENSE                 # File lisensi (opsional, bisa ditambahkan)


## Instruksi Instalasi

Untuk menjalankan program ini, ikuti langkah-langkah berikut:

1.  **Clone repositori:**
    Buka terminal atau Command Prompt, navigasi ke direktori tempat Anda ingin menyimpan proyek, lalu jalankan:
    ```bash
    git clone [URL_REPO_GITHUB_ANDA]
    cd [NAMA_FOLDER_PROYEK_ANDA]
    ```
    (Ganti `[URL_REPO_GITHUB_ANDA]` dengan URL repositori Anda dan `[NAMA_FOLDER_PROYEK_ANDA]` dengan nama folder yang dibuat oleh Git).

2.  **Buat dan aktifkan virtual environment (sangat disarankan):**
    ```bash
    python -m venv venv
    # Di Windows:
    venv\Scripts\activate
    # Di macOS/Linux:
    source venv/bin/activate
    ```

3.  **Upgrade `pip` (Penting!):**
    Untuk menghindari masalah instalasi, pastikan `pip` Anda adalah versi terbaru. Saat `venv` aktif, jalankan:
    * Di Windows (PowerShell):
        ```bash
        & ".\venv\Scripts\python.exe" -m pip install --upgrade pip
        ```
    * Di Windows (Command Prompt) / macOS / Linux:
        ```bash
        python -m pip install --upgrade pip
        ```

4.  **Instal semua dependensi:**
    ```bash
    pip install -r requirements.txt
    ```
    Model MediaPipe (`.tflite` atau `.task` files) akan diunduh secara otomatis ke direktori `models/` saat program pertama kali dijalankan (membutuhkan koneksi internet).

## Penggunaan Program

Setelah instalasi selesai, Anda dapat menjalankan program dengan perintah berikut:

```bash
python main.py
Program akan membuka jendela GUI yang menampilkan live feed video dari webcam Anda.

Sebuah kotak hijau akan muncul di area wajah bagian atas Anda (dahi), menunjukkan ROI untuk ekstraksi sinyal detak jantung (rPPG).
Sebuah kotak merah tipis akan muncul di sekitar bahu Anda, menunjukkan ROI untuk ekstraksi sinyal pernapasan.
Di panel kiri, Anda akan melihat dua grafik yang menampilkan sinyal rPPG dan sinyal pernapasan secara real-time.
Di atas grafik, detak jantung (Heart Rate) dan laju pernapasan (Respiration Rate) Anda akan ditampilkan dalam BPM (Beats/Breaths Per Minute), diperbarui secara dinamis.
Tips Penggunaan untuk Hasil Optimal:

Pastikan pencahayaan yang terang dan merata di wajah Anda untuk kualitas sinyal detak jantung yang lebih baik.
Minimalkan gerakan kepala dan tubuh yang tidak perlu (selain bernapas) untuk menjaga stabilitas sinyal.
Pastikan seluruh bahu dan dada Anda terlihat jelas di frame kamera agar deteksi pose untuk pernapasan akurat.