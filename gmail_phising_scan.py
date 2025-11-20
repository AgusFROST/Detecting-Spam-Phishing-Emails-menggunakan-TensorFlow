import os
import base64
import pickle
import re
import sys
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Agar output terminal mendukung UTF-8
sys.stdout.reconfigure(encoding='utf-8')

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# ===== WARNA TERMINAL (ANSII CODE) =====
colors = {
    "NORMAL": "\033[92m",    # Hijau
    "SPAM": "\033[93m",      # Kuning
    "PHISHING": "\033[91m"   # Merah
}
RESET = "\033[0m"

# ==========================================================
# CONFIG
# ==========================================================
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

MODEL_PATH = "model.h5"
TOKENIZER_PATH = "tokenizer.pkl"
SCALER_PATH = "scaler.pkl"
MAX_SEQUENCE_LENGTH = 200

# ==========================================================
# LOAD MODEL & OBJECTS
# ==========================================================
def load_artifacts():
    print("Loading model and objects...")

    model = load_model(MODEL_PATH)
    print("Model loaded")

    with open(TOKENIZER_PATH, "rb") as f:
        tokenizer = pickle.load(f)
    print("Tokenizer loaded")

    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
    print("Scaler loaded")

    return model, tokenizer, scaler

# ==========================================================
# GMAIL AUTHENTICATION
# ==========================================================
def authenticate_gmail():
    creds = None

    if os.path.exists('token.json'):
        with open('token.json', 'rb') as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                creds = None

        if not creds:
            print("Opening Google login page...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open('token.json', 'wb') as f:
            pickle.dump(creds, f)
        print("Token saved -> token.json")

    service = build('gmail', 'v1', credentials=creds)
    return service

# ==========================================================
# DECODE EMAIL BODY
# ==========================================================
def decode_email(payload):
    try:
        data = payload.get("body", {}).get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    except:
        pass

    if "parts" in payload:
        for part in payload["parts"]:
            result = decode_email(part)
            if result:
                return result

    return ""

# ==========================================================
# GET HEADER
# ==========================================================
def get_header(payload, name):
    headers = payload.get("headers", [])
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""

# ==========================================================
# CLEANING & FEATURE EXTRACTION
# ==========================================================
def clean_text(s):
    s = str(s).lower()
    s = re.sub(r'http\S+', ' URL ', s)
    s = re.sub(r'[^a-z0-9 ]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def extract_numeric_features(s):
    s = str(s)
    return [
        len(s),
        sum(c.isdigit() for c in s),
        sum(c.isupper() for c in s),
        len(re.findall(r'http[s]?://', s))
    ]

def preprocess_email(text, tokenizer, scaler):
    clean = clean_text(text)
    seq = tokenizer.texts_to_sequences([clean])
    padded = pad_sequences(seq, maxlen=MAX_SEQUENCE_LENGTH, padding='post')

    numeric = np.array([extract_numeric_features(text)])
    numeric_scaled = scaler.transform(numeric)

    return padded, numeric_scaled

# ==========================================================
# FINAL LABEL DECISION
# ==========================================================
def predict_email_label(pred_probs):
    phishing_thresh = 0.70
    spam_thresh = 0.65

    phishing_prob = pred_probs[2]
    spam_prob = pred_probs[1]

    if phishing_prob >= phishing_thresh:
        return "PHISHING"
    elif spam_prob >= spam_thresh:
        return "SPAM"
    else:
        return "NORMAL"

# ==========================================================
# SCAN GMAIL
# ==========================================================
def scan_gmail_user_input(save_file=True):
    model, tokenizer, scaler = load_artifacts()
    service = authenticate_gmail()

    # Label pilihan
    available_labels = {
        "1": ("INBOX", "Kotak Masuk"),
        "2": ("CATEGORY_PERSONAL", "Personal"),
        "3": ("CATEGORY_SOCIAL", "Sosial"),
        "4": ("CATEGORY_PROMOTIONS", "Promosi"),
        "5": ("CATEGORY_UPDATES", "Update"),
        "6": ("SPAM", "Spam")
    }

    print("\n=== Pilih label yang ingin discan ===")
    for key, (_, name) in available_labels.items():
        print(f"{key}. {name}")

    selected_keys = input("Masukkan nomor label (pisahkan koma) atau Enter untuk INBOX: ")
    selected_keys = [k.strip() for k in selected_keys.split(",") if k.strip() in available_labels]
    labels = [available_labels[k][0] for k in selected_keys] if selected_keys else ['INBOX']

    while True:
        try:
            max_results_input = int(input("Masukkan jumlah email yang ingin discan: "))
            if max_results_input <= 0:
                raise ValueError
            break
        except ValueError:
            print("Masukkan angka positif yang valid.")

    print(f"\nScanning label: {labels} ... (max {max_results_input} email)")

    all_messages = []
    next_page_token = None
    total_fetched = 0
    batch_size = 100

    while total_fetched < max_results_input:
        max_fetch = min(batch_size, max_results_input - total_fetched)
        response = service.users().messages().list(
            userId='me',
            maxResults=max_fetch,
            labelIds=labels,
            pageToken=next_page_token
        ).execute()

        messages = response.get('messages', [])
        if not messages:
            break

        all_messages.extend(messages)
        total_fetched += len(messages)
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    print(f"\nTotal email diambil: {len(all_messages)}")

    all_results = []

    for msg in all_messages:
        email = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        payload = email.get("payload", {})
        body = decode_email(payload)
        if not body.strip():
            continue

        sender = get_header(payload, "From")
        subject = get_header(payload, "Subject")

        X_text_seq, X_num = preprocess_email(body, tokenizer, scaler)
        prediction_probs = model.predict([X_text_seq, X_num])[0]
        label = predict_email_label(prediction_probs)

        snippet = email.get("snippet", "")[:80]

        color = colors.get(label, RESET)

        print("\n===============================")
        print(f"Email ID : {msg['id']}")
        print(f"From     : {sender}")
        print(f"Subject  : {subject}")
        print(f"Snippet  : {snippet}")
        print(
            f"Result   : {color}{label}{RESET} "
            f"(Prob: NORMAL={prediction_probs[0]:.2f}, SPAM={prediction_probs[1]:.2f}, "
            f"PHISHING={prediction_probs[2]:.2f})"
        )

        all_results.append({
            "email_id": msg['id'],
            "from": sender,
            "subject": subject,
            "snippet": snippet,
            "prediction_probs": prediction_probs.tolist(),
            "label": label
        })

    if save_file and all_results:
        df_results = pd.DataFrame(all_results)
        df_results.to_csv("scan_results.csv", index=False)
        df_results.to_json("scan_results.json", orient="records", force_ascii=False)
        print("\nHasil scan disimpan ke: scan_results.csv & scan_results.json")

if __name__ == "__main__":
    scan_gmail_user_input()
