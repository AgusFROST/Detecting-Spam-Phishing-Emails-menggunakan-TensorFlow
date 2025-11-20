# 🔍 Email Phishing Detection using TensorFlow + NLP

Project ini adalah sistem deteksi email phishing menggunakan Natural Language Processing (NLP) dan Deep Learning berbasis TensorFlow. Sistem dapat mempelajari pola email spam/phishing dan melakukan klasifikasi apakah sebuah email tergolong **ham (normal)** atau **spam/phishing**.

## 🚀 Fitur
- Preprocessing teks (lowercase, stopwords removal, stemming, dll)
- Ekstraksi fitur numerik dari teks email
- Arsitektur deep learning:
  - Embedding
  - Bi-LSTM
  - Dense Layer
- Model multi-input (teks + fitur numerik)
- Dapat memprediksi email baru
- Menyimpan model, tokenizer, dan scaler untuk inference

## 📂 Struktur Proyek

```
detecPhising/
│
├── phishing_detection.py       # Script utama training & prediksi
├── Emails.csv                  # Dataset contoh email
├── scaler.pkl                  # Model scaler untuk fitur numerik
├── tokenizer.pkl               # Tokenizer untuk teks
├── spam_phishing_model.h5      # Model hasil training
├── venv/                       # Virtual environment (opsional)
└── README.md                   # Dokumentasi proyek
```

## 📦 Requirements

Install library yang diperlukan:

```
pip install tensorflow nltk pandas numpy scikit-learn
```

## ▶️ Cara Menjalankan

1. Aktifkan Virtual Environment
```
venv\Scripts\activate
```

2. Jalankan script
```
python phishing_detection.py
```

3. Script akan:
- Load dataset
- Preprocessing
- Training model
- Menyimpan model & komponen pendukung
- Menampilkan hasil evaluasi

## 📊 Dataset

File `Emails.csv` berisi contoh email dengan format:

| label | text |
|---|---|
| ham | Please call me when you are free |
| spam | Your account is suspended, click here |

Kolom:
- `label` : `ham` atau `spam`
- `text` : isi email

## 🔍 Inference / Prediksi Email Baru

Model sudah siap untuk digunakan memprediksi teks baru.  
Contoh hasil output:

```
{
  "label": "spam",
  "probability": 0.78
}
```

## 📝 Catatan

- Dataset masih kecil, sehingga akurasi dapat meningkat jika ditambah dataset lebih besar.
- Model bisa disimpan dan dipakai ulang tanpa training ulang.

## 🧑‍💻 Pengembang

Agus – Developer Sistem Deteksi Phishing menggunakan Deep Learning

YogaGymn - Cyber Security

Tahun: 2025
