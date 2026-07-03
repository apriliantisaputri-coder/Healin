# Heal.In - Frontend

Frontend statis (HTML5, CSS3, JavaScript, Bootstrap 5) untuk sistem Heal.In,
sesuai rancangan pada proposal Bab 6d.

## Struktur

```
frontend/
├── index.html          # Homepage
├── questionnaire.html  # Formulir gejala bertahap (4 langkah)
├── result.html         # Halaman hasil skrining
├── css/style.css        # Design system (warna, tipografi, komponen)
└── js/
    ├── api.js            # Koneksi ke REST API Flask
    └── questionnaire.js  # Logic form bertahap + submit
```

## Cara menjalankan

1. **Jalankan backend Flask dulu** (lihat README.md utama), pastikan aktif
   di `http://127.0.0.1:5000`.
2. Buka folder `frontend/` ini dengan ekstensi **Live Server** di VS Code
   (klik kanan `index.html` → "Open with Live Server"), atau jalankan
   server statis sederhana:
   ```bash
   cd frontend
   python -m http.server 5500
   ```
   lalu buka `http://127.0.0.1:5500` di browser.
3. Klik "Mulai Skrining", isi formulir gejala, lalu lihat hasilnya.

## Catatan

- Alamat backend diatur di `js/api.js` lewat variabel `API_BASE_URL`
  (default: `http://127.0.0.1:5000`). Ganti kalau backend dijalankan di
  port/alamat lain.
- Backend Flask sudah diaktifkan CORS-nya (lihat `api/app.py`) supaya bisa
  dipanggil dari origin frontend yang berbeda (mis. port Live Server).
- Data hasil skrining dioper dari `questionnaire.html` ke `result.html`
  lewat `sessionStorage` (hilang otomatis saat tab ditutup).
