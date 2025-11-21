# 🔍 Email Spam Phishing Detection using TensorFlow + NLP

Project ini adalah sistem deteksi email phishing menggunakan Natural Language Processing (NLP) dan Deep Learning berbasis TensorFlow. Sistem dapat mempelajari pola email **NORMAL**, **SPAM**, atau **PHISHING** dan memprediksi email baru secara otomatis.

## 🚀 Fitur

* Preprocessing teks (lowercase, pembersihan URL, simbol, whitespace)
* Ekstraksi fitur numerik dari teks email (panjang teks, jumlah digit, huruf kapital, jumlah URL)
* Arsitektur deep learning:

  * Embedding
  * LSTM
  * Dense Layer
* Model multi-input (teks + fitur numerik)
* Scanning email Gmail secara langsung via API
* Hasil prediksi email ditampilkan di terminal dengan warna:

  * **NORMAL** → hijau
  * **SPAM** → kuning
  * **PHISHING** → merah
* Menyimpan hasil scan ke CSV dan JSON
* Menyimpan model, tokenizer, dan scaler untuk inference

## 📂 Struktur Proyek

```
detectPhishing/
│
├── gmail_phising_scan.py       # Script untuk scanning Gmail & prediksi
├── training_model.py           # Script utama training
├── emails.csv                  # Dataset contoh email
├── model.h5                    # Model hasil training
├── tokenizer.pkl               # Tokenizer untuk teks
├── scaler.pkl                  # Scaler untuk fitur numerik
├── token.json                  # Token autentikasi Gmail (otomatis dibuat)
├── credentials.json            # File OAuth Gmail API
├── venv/                       # Virtual environment (opsional)
└── README.md                   # Dokumentasi proyek
```

## 📦 Requirements

Install library yang diperlukan:

```bash
pip install tensorflow nltk pandas numpy scikit-learn google-api-python-client google-auth-httplib2 google-auth-oauthlib colorama
```

## ▶️ Cara Menjalankan

### 1. Training Model

```bash
python training_model.py
```

Script akan:

* Scan Gmail (opsional) dan menambah dataset
* Preprocessing teks dan ekstraksi fitur numerik
* Training model multi-input
* Menyimpan model (`model.h5`), tokenizer (`tokenizer.pkl`), dan scaler (`scaler.pkl`)

### 2. Scanning Email Gmail

```bash
python gmail_phising_scan.py
```

Script akan:

* Autentikasi Gmail via OAuth
* Pilih label Gmail (Inbox, Personal, Social, Promosi, Update, Spam)
* Menentukan jumlah email yang ingin discan
* Memprediksi setiap email
* Menampilkan hasil di terminal dengan warna sesuai label
* Menyimpan hasil scan ke `scan_results.csv` & `scan_results.json`

## 📊 Dataset

File `emails.csv` berisi contoh email dengan format:

| label    | text                                        |
| -------- | ------------------------------------------- |
| normal   | Please call me when you are free            |
| spam     | Your account is suspended, click here       |
| phishing | Urgent! Reset your password using this link |

Kolom:

* `label` : normal, spam, atau phishing
* `text`  : isi email

## 🔍 Contoh Output Scan Gmail

```
===============================
Email ID : 1789...
From     : someone@example.com
Subject  : Reset your password
Snippet  : Urgent! Click the link to reset your account...
Result   : PHISHING (Prob: NORMAL=0.10, SPAM=0.25, PHISHING=0.90)
```

Label muncul dengan warna terminal:

* NORMAL → hijau
* SPAM → kuning
* PHISHING → merah

## 📝 Catatan

* Dataset masih kecil, sehingga akurasi dapat meningkat jika menambah data lebih banyak.
* Model, tokenizer, dan scaler dapat digunakan ulang tanpa training ulang.
* Terminal harus mendukung ANSI color codes agar warna muncul.

## 🧑‍💻 Pengembang

Agus – Developer Sistem Deteksi Phishing menggunakan Deep Learning

YogaGymn – Cyber Security

Tahun: 2025
