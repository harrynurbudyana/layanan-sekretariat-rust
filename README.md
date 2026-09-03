# FIT E-Office (Rust + Svelte 5 Edition)

Implementasi ulang dan refactor performa tinggi dari sistem **Layanan Sekretariat Fakultas Ilmu Terapan (FIT) Telkom University** menggunakan **Rust (Axum + SQLx)** dan **Svelte 5 (Vite + Tailwind CSS)**.

## Keunggulan Stack Ini
- **Hemat RAM:** Backend hanya mengonsumsi **~12-15 MB RAM** (dibandingkan ~200-300MB pada Node.js/Next.js).
- **Embedded Web Server:** Axum langsung menyajikan REST API dan file statis Svelte 5.
- **Direct SQLite Access:** Membaca database `dev.db` (Surat/Unit) dan `rooms.db` (Peminjaman Ruangan) langsung via SQLx.
- **Svelte 5 Runes:** Frontend super reaktif dan ringan dengan bundle client hanya ~65 kB.

---

## Struktur Proyek

```text
layanan-sekretariat-rust/
├── backend/                    # Rust Web Server (Axum + SQLx)
│   ├── Cargo.toml
│   ├── .env                    # Konfigurasi port & path database
│   ├── data/                   # File SQLite (dev.db & rooms.db)
│   └── src/
│       └── main.rs             # Axum router, REST API handlers, static file serving
└── frontend/                   # Svelte 5 Web UI
    ├── package.json
    ├── vite.config.ts          # Proxy /api ke port 8080 saat development
    └── src/
        ├── App.svelte          # UI Dashboard, Agenda Surat, Ruangan, & Booking
        └── app.css             # Tailwind CSS styling
```

---

## Cara Menjalankan

### Mode Pengembangan (Development)

1. **Jalankan Backend Rust:**
   ```bash
   cd backend
   cargo run
   ```
   Server backend akan aktif di `http://localhost:8080`.

2. **Jalankan Frontend Svelte Dev Server (Tab Terminal Terpisah):**
   ```bash
   cd frontend
   npm run dev
   ```
   Buka `http://localhost:5173` di browser. Request `/api` akan otomatis di-proxy ke backend Rust.

---

### Mode Produksi (Single Binary Serving)

1. Build frontend statis:
   ```bash
   cd frontend
   npm run build
   ```
2. Build dan jalankan binary Rust:
   ```bash
   cd ../backend
   cargo run --release
   ```
3. Buka `http://localhost:8080`. Seluruh antarmuka web dan API backend berjalan dari satu proses binary Rust!

---

## API Endpoints yang Tersedia
- `GET /api/health`: Healthcheck sistem
- `GET /api/units`: Daftar Unit / Bagian / Prodi
- `GET /api/categories`: Daftar Kategori Perihal Surat
- `GET /api/letters`: Daftar Agenda Surat Keluar (dengan pagination & join)
- `GET /api/rooms`: Daftar Ruangan Rapat & Multimedia
- `GET /api/rooms/bookings`: Daftar Peminjaman Ruangan
