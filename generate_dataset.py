import csv
import random
import lorem
from datetime import datetime, timedelta

TOTAL_EMAILS = 5000
OUTPUT_FILE = "emails.csv"

# Dominasi bahasa 60% Indonesia, 40% English
def random_language():
    return random.choices(["id", "en"], weights=[0.6, 0.4])[0]

# Real company senders
real_senders = [
    "google.com","bri.co.id", "mandiri.co.id", "kemdikbud.go.id", "bca.co.id",
    "gmail.com", "tokopedia.com", "shopee.co.id", "amazon.com",
    "apple.com", "microsoft.com", "paypal.com", "linkedin.com",
    "booking.com"
]

# Malicious/fake domains
fake_senders = [
    "secure-login-confirm.net", "account-verification-alert.com",
    "id-update-security.cc", "data-update-login.info",
    "payment-claim-online.ru", "suspicious-access-alert.xyz"
]

subjects_normal = {
    "id": [
        "Informasi Pembayaran", "Notifikasi Sistem", "Konfirmasi Data",
        "Undangan Rapat", "Laporan Bulanan", "Pengumuman Resmi",
        "Tanda Terima"
    ],
    "en": [
        "Payment Information", "System Notification", "Data Confirmation",
        "Meeting Invitation", "Monthly Report", "Policy Update",
        "Receipt Confirmation"
    ]
}

subjects_spam = {
    "id": [
        "GRATIS Hadiah iPhone!", "Dapatkan uang sekarang",
        "Bonus saldo sampai 50 juta!", "Promo waktu terbatas!"
    ],
    "en": [
        "FREE iPhone Today!", "You just won $10,000!",
        "Limited Time Promotion", "Click now and get your reward!"
    ]
}

subjects_phishing = {
    "id": [
        "Akun Anda terblokir - Segera verifikasi",
        "Aktivitas mencurigakan terdeteksi",
        "Pembayaran tertunda - butuh tindakan",
        "Pembaruan keamanan wajib dilakukan"
    ],
    "en": [
        "Your account has been suspended",
        "Unusual sign-in detected",
        "Payment on hold – verification required",
        "Security update required"
    ]
}

def random_date():
    days = random.randint(0, 730)
    return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

def generate_body(label, lang):
    if label == "normal":
        if lang == "id":
            return (
                f"Halo,\n\n"
                f"{lorem.paragraph()}\n\n"
                f"Jika ada pertanyaan silakan balas email ini.\n\nTerima kasih."
            )
        else:
            return (
                f"Hello,\n\n"
                f"{lorem.paragraph()}\n\n"
                f"If you have any questions, feel free to reply to this email.\n\nThank you."
            )
    elif label == "spam":
        if lang == "id":
            return (
                f"SELAMAT!!! Anda menang undian nasional!\n"
                f"Kunjungi link berikut untuk klaim hadiah:\n"
                f"http://promo-{random.randint(1000,9999)}.click"
            )
        else:
            return (
                f"CONGRATULATIONS!!! You have been selected!\n"
                f"Claim your reward now:\n"
                f"http://reward-{random.randint(1000,9999)}.claim"
            )
    else:  # phishing
        fake_link = f"http://{random.choice(fake_senders)}/verify"
        if lang == "id":
            return (
                f"Penting!\n\n"
                f"Akun Anda terdeteksi aktivitas tidak wajar. "
                f"Harap verifikasi melalui tautan berikut:\n\n{fake_link}\n\n"
                f"Abaikan email ini jika sudah melakukan verifikasi."
            )
        else:
            return (
                f"Important!\n\n"
                f"Your account has detected unusual activity. "
                f"Please verify using the link below:\n\n{fake_link}\n\n"
                f"If you already verified, please ignore this email."
            )

rows = []

for _ in range(TOTAL_EMAILS):
    label = random.choices(
        ["normal", "spam", "phishing"],
        weights=[0.65, 0.20, 0.15]
    )[0]
    lang = random_language()

    if label == "normal":
        sender = f"noreply@{random.choice(real_senders)}"
        subject = random.choice(subjects_normal[lang])
    elif label == "spam":
        sender = f"promo@{random.choice(fake_senders)}"
        subject = random.choice(subjects_spam[lang])
    else:
        sender = f"security@{random.choice(fake_senders)}"
        subject = random.choice(subjects_phishing[lang])

    body = generate_body(label, lang)

    rows.append([
        random_date(),
        sender,
        subject,
        body,
        lang,
        label
    ])

# Tulis CSV
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "from", "subject", "body", "lang", "label"])
    writer.writerows(rows)

print(f"Dataset berhasil dibuat -> {OUTPUT_FILE}")
