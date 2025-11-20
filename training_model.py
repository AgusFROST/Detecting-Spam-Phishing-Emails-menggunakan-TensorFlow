import os
import re
import pickle
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Concatenate, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.utils import to_categorical

# ==========================================================
# CONFIG
# ==========================================================
MAX_WORDS = 10000
MAX_LEN = 200
MODEL_PATH = "model.h5"
TOKENIZER_PATH = "tokenizer.pkl"
SCALER_PATH = "scaler.pkl"
DATASET_CSV = "emails.csv"  # pakai dataset mock

# ==========================================================
# CLEAN TEKS & EXTRACT NUMERIC FEATURES
# ==========================================================
def clean_text(s):
    s = str(s).lower()
    s = re.sub(r'http\S+', ' URL ', s)
    s = re.sub(r'[^a-z0-9 ]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def extract_features(s):
    s = str(s)
    return [
        len(s),
        sum(c.isdigit() for c in s),
        sum(c.isupper() for c in s),
        len(re.findall(r'http[s]?://', s))
    ]

# ==========================================================
# TRAINING
# ==========================================================
def train_model():
    if not os.path.exists(DATASET_CSV):
        raise FileNotFoundError(f"Dataset {DATASET_CSV} tidak ditemukan!")

    df = pd.read_csv(DATASET_CSV)
    df = df.dropna(subset=['body', 'label'])  # pastikan kolom body ada
    df['clean'] = df['body'].apply(clean_text)

    label_mapping = {'normal':0, 'spam':1, 'phishing':2}
    df['label_num'] = df['label'].map(label_mapping)
    y = to_categorical(df['label_num'], num_classes=3)

    # Tokenizer
    tokenizer = Tokenizer(num_words=MAX_WORDS)
    tokenizer.fit_on_texts(df['clean'])
    sequences = tokenizer.texts_to_sequences(df['clean'])
    X_text = pad_sequences(sequences, maxlen=MAX_LEN, padding='post')
    with open(TOKENIZER_PATH, 'wb') as f:
        pickle.dump(tokenizer, f)

    # Numeric features
    X_numeric = np.array(df['body'].apply(extract_features).tolist())
    if X_numeric.shape[0] == 0:
        raise ValueError("Dataset kosong! Tambahkan email terlebih dahulu.")
    scaler = StandardScaler()
    X_numeric = scaler.fit_transform(X_numeric)
    with open(SCALER_PATH, 'wb') as f:
        pickle.dump(scaler, f)

    # Split data
    X_train_text, X_test_text, X_train_num, X_test_num, y_train, y_test = train_test_split(
        X_text, X_numeric, y, test_size=0.2, random_state=42, stratify=y
    )

    # Model
    text_input = Input(shape=(MAX_LEN,), name='text_input')
    x = Embedding(input_dim=MAX_WORDS, output_dim=64)(text_input)
    x = LSTM(64, dropout=0.2, recurrent_dropout=0.2)(x)
    num_input = Input(shape=(X_numeric.shape[1],), name='num_input')
    y2 = Dense(32, activation='relu')(num_input)
    combined = Concatenate()([x, y2])
    z = Dense(64, activation='relu')(combined)
    z = Dropout(0.3)(z)
    output = Dense(3, activation='softmax')(z)
    model = Model(inputs=[text_input, num_input], outputs=output)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    early = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    model.fit(
        {'text_input': X_train_text, 'num_input': X_train_num},
        y_train,
        validation_data=({'text_input': X_test_text, 'num_input': X_test_num}, y_test),
        epochs=15,
        batch_size=32,
        callbacks=[early],
        verbose=1
    )

    model.save(MODEL_PATH)
    print(f"Model tersimpan -> {MODEL_PATH}")
    print(f"Tokenizer tersimpan -> {TOKENIZER_PATH}")
    print(f"Scaler tersimpan -> {SCALER_PATH}")
    print("== TRAINING SELESAI ==")

# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    train_model()
