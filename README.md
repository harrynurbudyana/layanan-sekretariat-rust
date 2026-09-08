# FIT E-Office (Rust + Svelte 5 Edition)

Sistem Layanan Sekretariat Fakultas Ilmu Terapan (FIT) Telkom University yang dibangun dengan performa tinggi menggunakan **Rust (Axum + SQLx)** dan **Svelte 5 (Vite + Tailwind CSS)**.

Sistem ini mengelola:
1. **Generator & Agenda Surat Keluar**: Penomoran surat dinas otomatis berdasarkan unit kerja dan kategori surat.
2. **Peminjaman Ruangan & Workflow Approval**: Peminjaman ruangan rapat & multimedia dengan persetujuan bertingkat oleh **Admin Staf Sekretariat** serta notifikasi email otomatis ke admin dan pemohon.

---

## ⚡ Keunggulan Arsitektur

- **Super Hemat Sumber Daya:** Backend hanya mengonsumsi **~12–18 MB RAM** (jauh lebih ringan dibanding runtime Node.js/Next.js).
- **Single Process Serving:** Binary Axum menyajikan REST API (`/api/*`) sekaligus aset statis frontend Svelte 5 (`/`).
- **Direct SQLite Engine:** Menggunakan SQLx asynchronous pool membaca database lokal `dev.db` (surat & unit) dan `rooms.db` (ruangan & peminjaman).
- **Automated Email Notifications:** Integrasi SMTP asynchronous (Google Workspace / Gmail TLS) dengan template email notifikasi status peminjaman ruangan.

---

## 📋 Prasyarat Server (VPS Requirements)

Sebelum melakukan deployment ke Virtual Private Server (VPS), pastikan hal-hal berikut telah dipenuhi:

### 1. Spesifikasi Minimum Server
- **OS:** Linux (Ubuntu 22.04 LTS / 24.04 LTS atau Debian 12 direkomendasikan)
- **RAM:** Minimal 1 GB (Build Rust membutuhkan memori saat kompilasi release; jika RAM 1 GB, aktifkan Swap minimal 1–2 GB)
- **Storage:** Minimal 10 GB SSD
- **Akses:** Root atau user dengan hak akses `sudo`

### 2. Software / Perangkat Lunak yang Wajib Diinstal

| Komponen | Versi Minimal | Keterangan |
|---|---|---|
| **Build Tools** | - | `build-essential`, `pkg-config`, `libssl-dev`, `git`, `curl` |
| **Rust & Cargo** | **v1.85.0+** (Stable) | ⚠️ **PENTING:** Proyek menggunakan **Rust Edition 2024**. **JANGAN** gunakan `apt install rustc` dari distro Ubuntu/Debian karena versinya usang (< 1.85). Wajib gunakan **rustup**. |
| **Node.js & npm**| **v18.x** atau **v20.x LTS** | Diperlukan untuk kompilasi bundle frontend Svelte 5 |
| **Reverse Proxy**| **Caddy** *(Rekomendasi)* **atau Nginx** | **Caddy** otomatis mengurus HTTPS/SSL (Let's Encrypt) tanpa butuh Certbot. Jika memilih **Nginx**, diperlukan `certbot`. |

### 3. Akun Pengirim Email (SMTP)
- Akun Google Workspace / Gmail (misal: `e-office@tass.telkomuniversity.ac.id`).
- Aktifkan **2-Step Verification** pada akun Google tersebut.
- Buat **App Password (Sandi Aplikasi)** 16 digit melalui [Google Account Security](https://myaccount.google.com/apppasswords) dengan kategori *Mail*. Simpan 16 digit kode ini untuk konfigurasi `.env`.

---

## 🚀 Panduan Deployment Langkah-demi-Langkah di VPS

### Langkah 1: Persiapan Server & Dependensi Dasar

Hubungkan terminal ke VPS Anda via SSH, lalu perbarui sistem dan pasang tools pembangun:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git build-essential pkg-config libssl-dev
```

*(Opsional tapi Direkomendasikan)* Jika VPS Anda hanya memiliki 1 GB RAM, buat Swap file 2 GB agar proses kompilasi Rust berjalan lancar tanpa kehabisan memori:
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

### Langkah 2: Instalasi Rust (via Rustup)

Install Rust compiler versi terbaru melalui `rustup`:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
```

Pastikan versi Rust sudah terpasang dan minimal versi **1.85**:
```bash
rustc --version
# Output harus rustc 1.85.x atau yang lebih baru
```

---

### Langkah 3: Instalasi Node.js (v20 LTS)

Pasang Node.js menggunakan repositori resmi NodeSource:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node -v   # Pastikan v20.x
npm -v
```

---

### Langkah 4: Clone Repository Proyek

Clone kode sumber ke direktori yang diinginkan (misalnya `/var/www/layanan-sekretariat-rust`):

```bash
sudo git clone https://github.com/harrynurbudyana/layanan-sekretariat-rust.git /var/www/layanan-sekretariat-rust
sudo chown -R $USER:$USER /var/www/layanan-sekretariat-rust
cd /var/www/layanan-sekretariat-rust
```

---

### Langkah 5: Konfigurasi File Environment (`.env`)

Buat file konfigurasi `.env` di dalam folder `backend/`:

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

Sesuaikan parameter berikut:
```env
# Database SQLite (relatif dari folder eksekusi)
DATABASE_URL="sqlite://data/dev.db"
DATABASE_ROOMS_URL="sqlite://data/rooms.db"

# Port aplikasi backend Axum
PORT=8088

# Konfigurasi SMTP Email Notifikasi (Google Workspace / Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=e-office@tass.telkomuniversity.ac.id
SMTP_PASSWORD="qcia jkcd pqjw hcez"   # Ganti dengan 16 karakter App Password Anda
SMTP_FROM="E-Office Sekre FIT <e-office@tass.telkomuniversity.ac.id>"
SMTP_ADMIN_EMAIL=sekretariat@tass.telkomuniversity.ac.id
SMTP_ENABLED=true
```
> **Catatan Keamanan:** Jangan pernah melakukan `git commit` atau membagikan file `backend/.env` ke publik karena berisi kredensial email.

---

### Langkah 6: Build Frontend Svelte 5

Kompilasi aset antarmuka frontend menjadi file HTML/JS/CSS statis ke dalam folder `frontend/dist`:

```bash
cd /var/www/layanan-sekretariat-rust/frontend
npm install
npm run build
```
Pastikan folder `/var/www/layanan-sekretariat-rust/frontend/dist` telah berhasil terbentuk.

---

### Langkah 7: Build Binary Backend Rust (Release Mode)

Kompilasi backend Rust dalam mode `--release` untuk performa dan optimasi maksimal:

```bash
cd /var/www/layanan-sekretariat-rust/backend

# (Opsional) Uji coba pengiriman email dari terminal:
cargo run --bin test_email

# Kompilasi binary release
cargo build --release
```

Binary yang dihasilkan akan berada di `/var/www/layanan-sekretariat-rust/target/release/backend`.

---

### Langkah 8: Konfigurasi Service Systemd (Auto-Start & Restart)

Agar aplikasi berjalan di latar belakang secara otomatis saat VPS booting atau jika terjadi crash, buat unit service `systemd`:

```bash
sudo nano /etc/systemd/system/fit-eoffice.service
```

Tempelkan konfigurasi berikut (sesuaikan `User` dengan user non-root VPS Anda, misal `ubuntu` atau `deploy`):

```ini
[Unit]
Description=FIT E-Office Rust Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/var/www/layanan-sekretariat-rust/backend
ExecStart=/var/www/layanan-sekretariat-rust/target/release/backend
Restart=always
RestartSec=5
Environment=PORT=8088
Environment=RUST_LOG=backend=info,tower_http=info

# Batas file descriptor
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

Aktifkan dan jalankan service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable fit-eoffice
sudo systemctl start fit-eoffice
sudo systemctl status fit-eoffice
```

---

### Langkah 9: Konfigurasi Reverse Proxy & Domain SSL

Pilih salah satu dari dua opsi berikut untuk mengarahkan domain publik ke aplikasi:

#### 🌟 Opsi A: Menggunakan Caddy (SANGAT DIREKOMENDASIKAN)
> **Kelebihan Caddy:**
> - Konfigurasi hanya butuh **3 baris**.
> - **Otomatis SSL HTTPS** (Let's Encrypt / ZeroSSL) diterbitkan dan diperbarui otomatis tanpa perlu install Certbot atau setup cron.
> - Mendukung HTTP/2 dan HTTP/3 secara bawaan.

1. **Instal Caddy di Ubuntu / Debian:**
   ```bash
   sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
   curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
   curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
   sudo apt update
   sudo apt install -y caddy
   ```

2. **Edit file konfigurasi `/etc/caddy/Caddyfile`:**
   ```bash
   sudo nano /etc/caddy/Caddyfile
   ```
   Hapus isi defaultnya dan ganti dengan:
   ```caddy
   eoffice.tass.telkomuniversity.ac.id {
       reverse_proxy 127.0.0.1:8088
   }
   ```
   *(Ganti `eoffice.tass.telkomuniversity.ac.id` dengan nama domain yang mengarah ke IP VPS Anda)*

3. **Validasi & Reload Caddy:**
   ```bash
   sudo caddy validate --config /etc/caddy/Caddyfile
   sudo systemctl reload caddy
   ```
   *Selesai! Domain Anda langsung aktif dengan HTTPS yang aman dan valid.*

---

#### 🌐 Opsi B: Menggunakan Nginx + Certbot

Jika server Anda sudah memiliki Nginx yang sedang berjalan:

1. **Instal Nginx dan Certbot:**
   ```bash
   sudo apt install -y nginx certbot python3-certbot-nginx
   ```

2. **Buat file konfigurasi server block Nginx:**
   ```bash
   sudo nano /etc/nginx/sites-available/fit-eoffice
   ```

   Masukkan konfigurasi berikut:
   ```nginx
   server {
       listen 80;
       server_name eoffice.tass.telkomuniversity.ac.id;

       client_max_body_size 20M;

       # Gzip compression
       gzip on;
       gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

       location / {
           proxy_pass http://127.0.0.1:8088;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

3. **Aktifkan konfigurasi dan reload Nginx:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/fit-eoffice /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

4. **Pasang Sertifikat SSL HTTPS via Certbot:**
   ```bash
   sudo certbot --nginx -d eoffice.tass.telkomuniversity.ac.id
   ```

---

## 🛠️ Pemeliharaan & Monitoring (Maintenance)

### Melihat Log Real-Time Aplikasi
```bash
# Log backend Rust
sudo journalctl -u fit-eoffice -f

# Log Caddy (jika menggunakan Caddy)
sudo journalctl -u caddy -f

# Status Caddy
sudo systemctl status caddy
```

### Memeriksa Status Service
```bash
sudo systemctl status fit-eoffice
```

### Prosedur Update Kode (Deployment Ulang / Git Pull)
Jika ada pembaruan kode di GitHub:
```bash
cd /var/www/layanan-sekretariat-rust

# 1. Tarik kode terbaru
git pull origin main

# 2. Re-build frontend
cd frontend
npm install
npm run build

# 3. Re-build backend
cd ../backend
cargo build --release

# 4. Restart service
sudo systemctl restart fit-eoffice
```

### Backup Database SQLite
Database tersimpan di `backend/data/dev.db` dan `backend/data/rooms.db`. Buat cadangan secara berkala:
```bash
cp /var/www/layanan-sekretariat-rust/backend/data/*.db /path/ke/folder/backup/
```

---

## 💻 Panduan Menjalankan di Lokal (Local Development)

Jika ingin menjalankan aplikasi di komputer lokal untuk development:

### 1. Backend Rust
```bash
cd backend
cp .env.example .env
cargo run
```
Backend akan aktif di `http://localhost:8088`.

### 2. Frontend Svelte 5 (Vite Dev Server)
Buka tab terminal terpisah:
```bash
cd frontend
npm install
npm run dev
```
Buka `http://localhost:5173` di browser. Request API otomatis diteruskan ke port `8088`.
