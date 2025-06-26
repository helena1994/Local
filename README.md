# Bot Messenger Otomatis dengan Python 🤖

Bot Messenger otomatis yang dibangun dengan Python dan Selenium untuk memberikan respons otomatis berdasarkan analisis sentimen menggunakan TextBlob.

## 🚀 Fitur Utama

1. **Otomatisasi Messenger**: Membaca dan membalas pesan secara otomatis menggunakan Selenium
2. **Memori Percakapan**: Menyimpan riwayat interaksi dengan SQLite database
3. **Analisis Sentimen**: Menganalisis emosi pesan dengan TextBlob dan memberikan respons yang sesuai
4. **Auto-Login**: Login otomatis ke Facebook/Messenger dengan dukungan 2FA
5. **Respons Kontekstual**: Respons yang disesuaikan berdasarkan sentimen dan konteks percakapan

## 📁 Struktur Proyek

```
Local/
├── main.py                     # File utama untuk menjalankan bot
├── requirements.txt           # Dependencies Python
├── README.md                 # Dokumentasi
├── config/                   # Konfigurasi
│   ├── __init__.py
│   ├── settings.py          # Pengaturan bot
│   └── credentials_template.py  # Template kredensial login
├── database/                # Database SQLite
│   └── messenger_bot.db    # File database (dibuat otomatis)
└── scripts/                # Modul pendukung
    ├── __init__.py
    ├── messenger_automation.py  # Otomatisasi Messenger
    ├── auto_login.py           # Auto-login Facebook
    ├── sentiment_analysis.py   # Analisis sentimen
    └── database_manager.py     # Manajemen database
```

## ⚙️ Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/helena1994/Local.git
cd Local
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Download TextBlob Data
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('brown')"
```

### 4. Install ChromeDriver
- Download ChromeDriver dari [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)
- Extract dan pastikan `chromedriver` ada di PATH
- Atau gunakan `webdriver-manager` (sudah included dalam requirements)

### 5. Setup Kredensial
```bash
# Salin template kredensial
cp config/credentials_template.py config/credentials.py

# Edit kredensial dengan editor favorit
nano config/credentials.py
```

Edit `config/credentials.py` dengan data login Facebook Anda:
```python
FACEBOOK_CREDENTIALS = {
    'email': 'email_anda@example.com',
    'password': 'password_anda'
}
```

## 🔧 Konfigurasi

### Pengaturan Bot (config/settings.py)

```python
# Interval pengecekan pesan (detik)
BOT_CONFIG = {
    'check_interval': 5,
    'response_delay': (2, 5),  # Delay respons (min, max)
    'headless': False,         # True untuk mode headless
}

# Threshold analisis sentimen
SENTIMENT_CONFIG = {
    'threshold_positive': 0.1,
    'threshold_negative': -0.1,
}
```

### Template Respons

Anda dapat mengkustomisasi respons bot berdasarkan sentimen di `config/settings.py`:

```python
RESPONSE_TEMPLATES = {
    'positive': [
        "Senang mendengar itu! 😊",
        "Wah, bagus sekali! 👍",
    ],
    'negative': [
        "Maaf mendengar itu. Semoga cepat membaik 🙏",
        "Saya ikut prihatin. Tetap semangat ya! 💪",
    ],
    'neutral': [
        "Terima kasih sudah mengirim pesan! 😊",
        "Baik, saya mengerti 👍",
    ]
}
```

## 🚀 Cara Menjalankan

### Menjalankan Bot
```bash
python main.py
```

### Mode Headless (Background)
Edit `config/settings.py`:
```python
BOT_CONFIG = {
    'headless': True,  # Set True untuk mode headless
}
```

## 📊 Database

Bot menggunakan SQLite untuk menyimpan:

- **messages**: Riwayat pesan masuk dan keluar
- **users**: Data pengguna dan preferensi
- **activity_log**: Log aktivitas bot

### Struktur Database

#### Tabel Messages
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| user_id | TEXT | ID pengguna |
| user_name | TEXT | Nama pengguna |
| message_text | TEXT | Isi pesan |
| message_type | TEXT | 'incoming' atau 'outgoing' |
| sentiment_score | REAL | Skor sentimen (-1 to 1) |
| sentiment_label | TEXT | 'positive', 'negative', 'neutral' |
| timestamp | DATETIME | Waktu pesan |

## 🎯 Analisis Sentimen

Bot menggunakan dua metode analisis sentimen:

1. **TextBlob**: Analisis sentimen berbasis machine learning
2. **Kamus Kata Indonesia**: Analisis berdasarkan kata-kata sentimen bahasa Indonesia

### Contoh Analisis
```python
# Pesan positif
"Senang sekali hari ini!" → Score: 0.8 (positive)

# Pesan negatif  
"Hari ini sedih banget" → Score: -0.6 (negative)

# Pesan netral
"Apa kabar?" → Score: 0.0 (neutral)
```

## 🔐 Keamanan

### Two-Factor Authentication (2FA)
Jika akun Facebook menggunakan 2FA, aktifkan di `config/credentials.py`:
```python
SECURITY_CONFIG = {
    'enable_2fa_handling': True,
    'trusted_device': True
}
```

### Tips Keamanan
- Jangan commit file `credentials.py` ke repository
- Gunakan akun Facebook terpisah khusus untuk bot
- Aktifkan 2FA untuk keamanan tambahan
- Monitor aktivitas login di Facebook Security Settings

## 🐛 Troubleshooting

### Error Common

#### 1. ChromeDriver tidak ditemukan
```bash
# Install chromedriver via package manager
# Ubuntu/Debian:
sudo apt-get install chromium-chromedriver

# macOS:
brew install chromedriver
```

#### 2. Login gagal
- Periksa credentials di `config/credentials.py`
- Pastikan tidak ada Captcha atau security check
- Coba login manual di browser terlebih dahulu

#### 3. Element tidak ditemukan
- Facebook sering mengubah selectors
- Update selectors di `config/credentials.py` jika perlu
- Jalankan dalam mode non-headless untuk debugging

#### 4. Database error
```bash
# Reset database jika corrupt
rm database/messenger_bot.db
python main.py  # Database akan dibuat ulang
```

### Debug Mode
Untuk debugging, aktifkan logging detail:
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 📝 Logs

Bot menyimpan log aktivitas di:
- **Console**: Output real-time
- **bot.log**: File log dengan rotasi otomatis
- **Database**: Log aktivitas tersimpan di tabel `activity_log`

## 🤝 Kontribusi

1. Fork repository
2. Buat branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add: Amazing Feature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📄 Lisensi

Project ini menggunakan MIT License. Lihat file `LICENSE` untuk detail.

## ⚠️ Disclaimer

- Bot ini dibuat untuk tujuan edukasi dan personal use
- Pastikan mengikuti Terms of Service Facebook/Messenger
- Gunakan dengan bijak dan tidak untuk spam
- Developer tidak bertanggung jawab atas penyalahgunaan bot

## 🆘 Support

Jika mengalami masalah:
1. Cek bagian Troubleshooting di atas
2. Lihat issue yang sudah ada di GitHub
3. Buat issue baru dengan detail error

## 📚 Referensi

- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [TextBlob Documentation](https://textblob.readthedocs.io/)
- [SQLite Documentation](https://docs.python.org/3/library/sqlite3.html)
- [Facebook Messenger](https://www.messenger.com/)

---

**Dibuat dengan ❤️ menggunakan Python**