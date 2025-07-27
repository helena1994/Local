# Local

## Facebook Messenger Bot + SOCKS5 Proxy Server

Repository ini menyediakan dua fitur utama:
1. **Facebook Messenger Bot** - Bot otomatis untuk membalas pesan di Facebook Messenger
2. **SOCKS5 Proxy Server** - Server proxy dengan kontrol bandwidth (BPS)

### Facebook Messenger Bot

Bot otomatis untuk membalas pesan di Facebook Messenger menggunakan Selenium, tanpa API. Bot ini dapat melakukan login otomatis, membaca pesan yang belum dibaca, dan memberikan balasan otomatis.

#### Fitur Messenger Bot

1. **Login Otomatis**: Menggunakan Selenium untuk login ke Facebook secara otomatis
2. **Navigasi ke Messenger**: Membuka dan mengakses halaman Messenger
3. **Deteksi Pesan Belum Dibaca**: Mengidentifikasi percakapan dengan pesan yang belum dibaca
4. **Balasan Otomatis**: Mengirim balasan dengan teks yang telah ditentukan
5. **Error Handling**: Penanganan error yang robust untuk keandalan
6. **Logging**: Sistem logging lengkap untuk monitoring dan debugging

### SOCKS5 Proxy Server

Server proxy SOCKS5 dengan kontrol bandwidth (BPS - Bytes Per Second) yang dapat digunakan untuk membatasi kecepatan koneksi internet.

#### Fitur SOCKS5 Proxy

1. **SOCKS5 Protocol**: Implementasi lengkap protokol SOCKS5 (RFC 1928)
2. **Bandwidth Throttling**: Kontrol kecepatan transfer data (BPS)
3. **Burst Control**: Izin burst untuk koneksi singkat
4. **Multi-threading**: Mendukung multiple koneksi bersamaan
5. **Connection Logging**: Log semua koneksi dan transfer data
6. **Configurable**: Konfigurasi melalui environment variables atau command line

### Prasyarat

1. **Python 3.7+** (direkomendasikan Python 3.8+)
2. **Google Chrome Browser** (versi terbaru) - untuk Messenger Bot
3. **ChromeDriver** (akan diunduh otomatis oleh webdriver-manager) - untuk Messenger Bot
4. **Akun Facebook** dengan kredensial login - untuk Messenger Bot

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
# Facebook Messenger Bot
FACEBOOK_EMAIL=your_facebook_email@example.com
FACEBOOK_PASSWORD=your_facebook_password
AUTO_REPLY_MESSAGE=Terima kasih atas pesan Anda! Saya akan membalas sesegera mungkin.

# SOCKS5 Proxy Server
PROXY_HOST=127.0.0.1
PROXY_PORT=1080
MAX_BYTES_PER_SECOND=0
BURST_SIZE=0
```

### Penggunaan

#### Menjalankan SOCKS5 Proxy Server

##### Proxy dengan bandwidth unlimited (default)
```bash
python3 run_proxy.py
```

##### Proxy dengan bandwidth 1 MB/s
```bash
python3 run_proxy.py --bps 1048576
```

##### Proxy dengan bandwidth 100 KB/s dan burst 500 KB
```bash
python3 run_proxy.py --bps 102400 --burst 512000
```

##### Proxy pada host dan port custom
```bash
python3 run_proxy.py --host 0.0.0.0 --port 8080
```

##### Menggunakan npm scripts
```bash
npm run start:proxy                 # Default settings
npm run start:proxy:limited         # 1 MB/s limit
npm run check:proxy                 # Check configuration
```

#### Menjalankan Bot Messenger

```bash
cd src
python3 messenger_bot.py
```

##### Atau menggunakan wrapper script
```bash
python3 run_bot.py
python3 run_bot.py --headless       # Headless mode
```

#### Menjalankan Bot Telegram (Existing)

```bash
npm start
```

### Konfigurasi Environment Variables

#### Messenger Bot Variables

| Variable | Deskripsi | Default | Required |
|----------|-----------|---------|----------|
| `FACEBOOK_EMAIL` | Email Facebook untuk login | - | ✅ |
| `FACEBOOK_PASSWORD` | Password Facebook | - | ✅ |
| `AUTO_REPLY_MESSAGE` | Pesan balasan otomatis | "Terima kasih..." | ❌ |
| `HEADLESS_MODE` | Jalankan browser tanpa UI | False | ❌ |
| `IMPLICIT_WAIT` | Timeout menunggu element (detik) | 10 | ❌ |
| `PAGE_LOAD_TIMEOUT` | Timeout loading halaman (detik) | 30 | ❌ |

#### SOCKS5 Proxy Variables

| Variable | Deskripsi | Default | Required |
|----------|-----------|---------|----------|
| `PROXY_HOST` | Host untuk bind server | 127.0.0.1 | ❌ |
| `PROXY_PORT` | Port untuk bind server | 1080 | ❌ |
| `MAX_BYTES_PER_SECOND` | Limit bandwidth (bytes/detik) | 0 (unlimited) | ❌ |
| `BURST_SIZE` | Ukuran burst (bytes) | 0 | ❌ |
| `RESET_INTERVAL` | Interval reset counter (detik) | 1.0 | ❌ |
| `MAX_CONNECTIONS` | Maksimum koneksi bersamaan | 100 | ❌ |
| `CONNECTION_TIMEOUT` | Timeout koneksi (detik) | 10 | ❌ |
| `LOG_LEVEL` | Level logging | INFO | ❌ |

### Struktur Project

```
Local/
├── src/
│   ├── messenger_bot.py    # Bot Messenger (Python)
│   ├── config.py          # Konfigurasi messenger bot
│   ├── socks5_proxy.py    # SOCKS5 Proxy Server
│   ├── proxy_config.py    # Konfigurasi proxy server
│   ├── bot.js             # Bot Telegram (JavaScript)
│   ├── bot1.js            # Bot Telegram variant
│   └── Sheets.js          # Google Sheets integration
├── credentials/           # Service account credentials
├── run_bot.py            # Messenger bot runner
├── run_proxy.py          # SOCKS5 proxy runner
├── test_messenger_bot.py # Messenger bot tests
├── test_proxy.py         # SOCKS5 proxy tests
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
├── .env.example          # Template environment variables
└── README.md             # Dokumentasi ini
```

### Testing

#### Test Messenger Bot
```bash
npm run test:messenger
# atau
PYTHONPATH=src python3 test_messenger_bot.py
```

#### Test SOCKS5 Proxy
```bash
npm run test:proxy
# atau
PYTHONPATH=src python3 test_proxy.py
```

### Contoh Penggunaan SOCKS5 Proxy

#### Menggunakan proxy dengan curl
```bash
# Jalankan proxy server
python3 run_proxy.py --bps 1048576  # 1 MB/s limit

# Di terminal lain, gunakan curl dengan proxy
curl --socks5 127.0.0.1:1080 http://httpbin.org/ip
```

#### Menggunakan proxy dengan aplikasi Python
```python
import requests

proxies = {
    'http': 'socks5://127.0.0.1:1080',
    'https': 'socks5://127.0.0.1:1080'
}

response = requests.get('http://httpbin.org/ip', proxies=proxies)
print(response.json())
```

#### Bandwidth Control Examples

```bash
# Unlimited bandwidth (default)
python3 run_proxy.py

# 100 KB/s limit
python3 run_proxy.py --bps 102400

# 1 MB/s with 500 KB burst
python3 run_proxy.py --bps 1048576 --burst 512000

# Custom host and port
python3 run_proxy.py --host 0.0.0.0 --port 8080
```

### Keamanan dan Best Practices

#### Messenger Bot
1. **Jangan commit file `.env`** - sudah ada di `.gitignore`
2. **Gunakan password yang kuat** untuk akun Facebook
3. **Aktifkan 2FA di Facebook** untuk keamanan tambahan
4. **Jalankan bot di environment yang aman**
5. **Monitor log files** untuk aktivitas yang mencurigakan

#### SOCKS5 Proxy
1. **Jangan expose proxy ke internet** - gunakan di localhost atau network internal
2. **Monitor bandwidth usage** - cek log untuk penggunaan yang tidak wajar
3. **Gunakan firewall** untuk membatasi akses ke proxy
4. **Set limits yang wajar** - bandwidth throttling untuk mencegah abuse
5. **Log semua koneksi** - monitor siapa yang menggunakan proxy

### Troubleshooting

#### Messenger Bot Issues

##### Bot tidak bisa login
- Pastikan kredensial Facebook benar
- Cek apakah akun memerlukan verifikasi 2FA
- Facebook mungkin memblokir login otomatis - coba login manual terlebih dahulu

##### Element tidak ditemukan
- Facebook sering mengubah struktur DOM
- Update selector di `config.py` sesuai struktur terbaru
- Gunakan browser developer tools untuk inspect element

##### ChromeDriver issues
- Pastikan Chrome browser terinstall
- Webdriver-manager akan mengunduh ChromeDriver otomatis
- Jika error, coba hapus cache webdriver: `rm -rf ~/.wdm`

##### Bot berjalan lambat
- Sesuaikan `IMPLICIT_WAIT` dan `PAGE_LOAD_TIMEOUT`
- Gunakan `HEADLESS_MODE=True` untuk performa lebih baik
- Pastikan koneksi internet stabil

#### SOCKS5 Proxy Issues

##### Proxy tidak bisa start
- Pastikan port tidak digunakan oleh aplikasi lain
- Cek permission untuk bind ke port (< 1024 perlu sudo)
- Gunakan `netstat -tlpn | grep :1080` untuk cek port usage

##### Connection refused
- Pastikan proxy server berjalan
- Cek firewall settings
- Verifikasi host dan port configuration

##### Bandwidth throttling tidak bekerja
- Pastikan nilai BPS > 0
- Cek konfigurasi burst size
- Monitor log untuk melihat throttling activity

##### Performance issues
- Sesuaikan MAX_CONNECTIONS untuk concurrent users
- Tuning CONNECTION_TIMEOUT sesuai kebutuhan
- Consider menggunakan dedicated server untuk high traffic

### Logging

#### Messenger Bot Logging
Bot akan membuat file log `messenger_bot.log` yang berisi:
- Informasi login dan navigasi
- Status percakapan yang diproses
- Error dan exception yang terjadi
- Statistik balasan yang berhasil dikirim

#### SOCKS5 Proxy Logging
Proxy server akan membuat file log `socks5_proxy.log` yang berisi:
- Informasi koneksi client
- Detail target connections
- Bandwidth throttling activity
- Transfer statistics
- Error dan troubleshooting info

### Compliance dan Legal

⚠️ **Penting**: 

#### Messenger Bot
- Bot ini menggunakan browser automation, bukan API resmi Facebook
- Pastikan penggunaan sesuai dengan Terms of Service Facebook
- Gunakan dengan bijak dan tidak untuk spam
- Hormati privasi dan consent penerima pesan

#### SOCKS5 Proxy
- Proxy server ini untuk keperluan development dan testing
- Jangan gunakan untuk melanggar Terms of Service website/layanan
- Pastikan comply dengan hukum dan regulasi setempat
- Gunakan bandwidth throttling secara bertanggung jawab

### Contributing

1. Fork repository
2. Buat feature branch
3. Commit changes dengan pesan yang jelas
4. Push ke branch
5. Buat Pull Request

### License

[Sesuaikan dengan license yang diinginkan]