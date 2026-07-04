# Heal.In - Frontend

Frontend statis (HTML5, CSS3, JavaScript, Bootstrap 5) untuk sistem Heal.In,
sesuai rancangan pada proposal Bab 6d.

## Struktur

```
frontend/
├── index.html            # Homepage
├── questionnaire.html    # Formulir gejala bertahap (4 langkah)
├── result.html           # Halaman hasil skrining
├── css/style.css          # Design system (warna, tipografi, komponen)
└── js/
    ├── skrining-engine.js # Mesin inferensi forward chaining (JS, jalan di browser)
    ├── api.js              # Helper (skrining = lokal; history/login = REST API Flask)
    └── questionnaire.js    # Logic form bertahap + submit
```

## Cara menjalankan (TIDAK PERLU backend untuk melihat hasil skrining)

Sejak `frontend/js/skrining-engine.js` ditambahkan, proses skrining
(isi formulir → lihat hasil) dihitung **langsung di browser** dan tidak
lagi memanggil backend Flask sama sekali. Jadi cukup:

1. Buka `frontend/index.html` langsung (double-click, tidak perlu Live
   Server / `python -m http.server` / menjalankan Flask).
2. Klik "Mulai Skrining", isi formulir gejala, klik "Lihat Hasil" →
   hasil langsung muncul di `result.html`, tanpa loading/koneksi ke
   server apa pun.

## Catatan

- `js/skrining-engine.js` adalah porting 1:1 dari mesin Experta di
  `engine/` + `rules/*.py`, sudah diuji cocok 100% terhadap versi
  Python-nya (skor & kondisi identik untuk seluruh kombinasi gejala).
  Kalau aturan di `rules/*.py` diubah, `skrining-engine.js` perlu
  disesuaikan juga secara manual.
- Backend Flask (`api/app.py`) sekarang OPSIONAL, hanya dipakai untuk
  fitur **Login & Riwayat Pemeriksaan (History)** yang memang butuh
  database PostgreSQL untuk menyimpan data lintas sesi. Kalau backend
  tidak dijalankan, fitur skrining tetap berfungsi penuh; hanya
  riwayat yang tidak akan tersimpan.
- Alamat backend (untuk History) diatur di `js/api.js` lewat variabel
  `API_BASE_URL` (default: `http://127.0.0.1:5000`).
- Data hasil skrining dioper dari `questionnaire.html` ke `result.html`
  lewat `sessionStorage` (hilang otomatis saat tab ditutup).
