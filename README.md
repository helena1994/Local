# Local

## Facebook Messenger Bot

Bot otomatis untuk membalas pesan di Facebook Messenger menggunakan Selenium, tanpa API. Bot ini dapat melakukan login otomatis, membaca pesan yang belum dibaca, dan memberikan balasan otomatis.

### Fitur Utama

1. **Login Otomatis**: Menggunakan Selenium untuk login ke Facebook secara otomatis
2. **Navigasi ke Messenger**: Membuka dan mengakses halaman Messenger
3. **Deteksi Pesan Belum Dibaca**: Mengidentifikasi percakapan dengan pesan yang belum dibaca
4. **Balasan Otomatis**: Mengirim balasan dengan teks yang telah ditentukan
5. **Error Handling**: Penanganan error yang robust untuk keandalan
6. **Logging**: Sistem logging lengkap untuk monitoring dan debugging

### Prasyarat

1. **Python 3.7+** (direkomendasikan Python 3.8+)
2. **Google Chrome Browser** (versi terbaru)
3. **ChromeDriver** (akan diunduh otomatis oleh webdriver-manager)
4. **Akun Facebook** dengan kredensial login

### Instalasi

1. Clone repository ini:
```bash
git clone <repository-url>
cd Local
```

2. Install dependencies Python:
```bash
pip install -r requirements.txt
```

3. Setup environment variables:
```bash
cp .env.example .env
```

4. Edit file `.env` dan isi dengan kredensial Facebook Anda:
```env
FACEBOOK_EMAIL=your_facebook_email@example.com
FACEBOOK_PASSWORD=your_facebook_password
AUTO_REPLY_MESSAGE=Terima kasih atas pesan Anda! Saya akan membalas sesegera mungkin.
```

### Penggunaan

#### Menjalankan Bot Messenger

**Lokal (satu kali):**
```bash
cd src
python3 messenger_bot.py
```

**VPS (mode daemon):**
```bash
python3 run_bot.py --headless --daemon
```

#### Menjalankan Bot Telegram (Existing)

```bash
npm start
```

### Deployment VPS

Untuk deployment di VPS (Virtual Private Server), gunakan salah satu metode berikut:

#### 🚀 Quick Install (Recommended)
```bash
git clone <repository-url>
cd Local
chmod +x install_vps.sh
./install_vps.sh
```

#### 🐳 Docker Deployment
```bash
git clone <repository-url>
cd Local
cp .env.example .env
# Edit .env dengan kredensial Anda
docker-compose up -d
```

**Lihat panduan lengkap:** [VPS_DEPLOYMENT.md](VPS_DEPLOYMENT.md)

### Konfigurasi Environment Variables

| Variable | Deskripsi | Default | Required |
|----------|-----------|---------|----------|
| `FACEBOOK_EMAIL` | Email Facebook untuk login | - | ✅ |
| `FACEBOOK_PASSWORD` | Password Facebook | - | ✅ |
| `AUTO_REPLY_MESSAGE` | Pesan balasan otomatis | "Terima kasih..." | ❌ |
| `HEADLESS_MODE` | Jalankan browser tanpa UI | False | ❌ |
| `DAEMON_MODE` | Mode daemon untuk VPS | False | ❌ |
| `CHECK_INTERVAL` | Interval cek pesan (detik) | 300 | ❌ |
| `IMPLICIT_WAIT` | Timeout menunggu element (detik) | 10 | ❌ |
| `PAGE_LOAD_TIMEOUT` | Timeout loading halaman (detik) | 30 | ❌ |

### Struktur Project

```
Local/
├── src/
│   ├── messenger_bot.py    # Bot Messenger (Python)
│   ├── config.py          # Konfigurasi bot
│   ├── bot.js             # Bot Telegram (JavaScript)
│   ├── bot1.js            # Bot Telegram variant
│   └── Sheets.js          # Google Sheets integration
├── credentials/           # Service account credentials
├── logs/                  # Log files (created automatically)
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
├── .env.example          # Template environment variables
├── Dockerfile            # Docker container configuration
├── docker-compose.yml    # Docker Compose for easy deployment
├── messenger-bot.service # Systemd service for VPS
├── install_vps.sh        # VPS installation script
├── health_check.py       # Health monitoring script
├── VPS_DEPLOYMENT.md     # VPS deployment guide
└── README.md             # Dokumentasi ini
```

### Keamanan dan Best Practices

1. **Jangan commit file `.env`** - sudah ada di `.gitignore`
2. **Gunakan password yang kuat** untuk akun Facebook
3. **Aktifkan 2FA di Facebook** untuk keamanan tambahan
4. **Jalankan bot di environment yang aman**
5. **Monitor log files** untuk aktivitas yang mencurigakan

### Troubleshooting

#### Bot tidak bisa login
- Pastikan kredensial Facebook benar
- Cek apakah akun memerlukan verifikasi 2FA
- Facebook mungkin memblokir login otomatis - coba login manual terlebih dahulu

#### Element tidak ditemukan
- Facebook sering mengubah struktur DOM
- Update selector di `config.py` sesuai struktur terbaru
- Gunakan browser developer tools untuk inspect element

#### ChromeDriver issues
- Pastikan Chrome browser terinstall
- Webdriver-manager akan mengunduh ChromeDriver otomatis
- Jika error, coba hapus cache webdriver: `rm -rf ~/.wdm`

#### Bot berjalan lambat
- Sesuaikan `IMPLICIT_WAIT` dan `PAGE_LOAD_TIMEOUT`
- Gunakan `HEADLESS_MODE=True` untuk performa lebih baik
- Pastikan koneksi internet stabil

### Logging

Bot akan membuat file log `messenger_bot.log` yang berisi:
- Informasi login dan navigasi
- Status percakapan yang diproses
- Error dan exception yang terjadi
- Statistik balasan yang berhasil dikirim

### Compliance dan Legal

⚠️ **Penting**: 
- Bot ini menggunakan browser automation, bukan API resmi Facebook
- Pastikan penggunaan sesuai dengan Terms of Service Facebook
- Gunakan dengan bijak dan tidak untuk spam
- Hormati privasi dan consent penerima pesan

### Contributing

1. Fork repository
2. Buat feature branch
3. Commit changes dengan pesan yang jelas
4. Push ke branch
5. Buat Pull Request

### License

[Sesuaikan dengan license yang diinginkan]