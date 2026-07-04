

<video src="https://github.com/user-attachments/assets/967d0354-057f-45ba-a227-7f0a5f2d1856" width="100%" controls></video>



# Heal.In - Backend (Sistem Pakar Forward Chaining)

Source code mesin inferensi & REST API untuk sistem pakar Heal.In
("Sistem Pakar Pemeriksaan Kesehatan Mental Mahasiswa: Berbasis
Forward Chaining & Rule-Based Reasoning"), sesuai rancangan pada
proposal (Bab 5-7).

## Struktur folder

```
healin_backend/
├── engine/
│   ├── compat.py            # patch kompatibilitas Experta utk Python 3.10+
│   ├── facts.py              # Fact: Gejala, Kondisi
│   └── knowledge_engine.py   # HealInEngine (forward chaining)
├── rules/
│   ├── gejala_list.py        # daftar 13 gejala valid (fisik/kognitif/emosional/perilaku)
│   ├── normal_rules.py       # aturan kondisi Normal
│   ├── stres_ringan_rules.py # aturan kondisi Stres Ringan
│   ├── stres_berat_rules.py  # aturan kondisi Stres Berat
│   ├── kecemasan_rules.py    # aturan kondisi Kecemasan
│   ├── depresi_rules.py      # aturan kondisi Potensi Depresi
│   └── rekomendasi.py        # rekomendasi tindak lanjut per kondisi
├── api/
│   └── app.py                 # REST API Flask (/api/skrining, /api/gejala)
├── models/
│   └── models.py               # skema SQLAlchemy (PostgreSQL)
├── demo.py                     # demo CLI skenario "Andi" dari proposal
├── test_engine.py              # unit test rule engine (pytest)
└── requirements.txt
```

## Database (PostgreSQL)

Sejak migrasi database, Heal.In menggunakan **PostgreSQL** sebagai
database utama (lihat `models/models.py`, `config.py`). Rule engine
Experta, endpoint `/api/gejala` dan `/api/skrining`, serta seluruh
tampilan frontend **tidak berubah** dan tidak bergantung pada database
ini -- database menjadi fondasi untuk fitur Login, History, Dashboard,
dan penyimpanan hasil skrining ke depannya.

1. Salin `.env.example` menjadi `.env` lalu sesuaikan kredensial:

   ```bash
   cp .env.example .env
   ```

2. Buat database PostgreSQL:

   ```bash
   createdb healin_db
   ```

3. Jalankan migrasi (skema tabel: `users`, `symptoms`, `conditions`,
   `rules`, `recommendations`, `examination_history`, serta tabel lama
   `pengguna` & `sesi_pemeriksaan` yang tetap dipertahankan):

   ```bash
   flask --app api.app db upgrade
   ```

   Jika folder `migrations/` belum ada di clone Anda (mis. clone baru
   tanpa histori migrasi sebelumnya), jalankan dulu:

   ```bash
   flask --app api.app db init
   flask --app api.app db migrate -m "Initial migration"
   flask --app api.app db upgrade
   ```

4. Isi data awal (gejala, kondisi, aturan, rekomendasi):

   ```bash
   python seed.py
   ```

Jika koneksi PostgreSQL gagal (mis. server belum menyala), aplikasi
akan tetap berjalan dan mencetak pesan error yang jelas di log --
endpoint skrining tidak terpengaruh, hanya fitur yang butuh database
yang belum bisa berfungsi.

## Menjalankan

```bash
pip install -r requirements.txt

createdb healin_db
flask --app api.app db upgrade
python seed.py

# Demo cepat lewat terminal
python demo.py

# Unit test
pytest test_engine.py -v

# Jalankan REST API (http://localhost:5000)
flask run
# atau: python api/app.py
```

## Catatan penting: kompatibilitas Experta

Library `experta` terakhir dirilis untuk Python < 3.10 dan memakai
`collections.Mapping` yang sejak Python 3.10 dipindah ke
`collections.abc.Mapping`. `engine/compat.py` berisi patch kecil yang
menambal ini secara otomatis -- **wajib tetap ada** apabila proyek
dijalankan di Python 3.10/3.11/3.12.

## Contoh pemakaian endpoint

```bash
curl -X POST http://localhost:5000/api/skrining \
  -H "Content-Type: application/json" \
  -d '{"gejala": ["sulit_tidur", "cemas_berlebihan", "sulit_konsentrasi"]}'
```

Response:
```json
{
  "kondisi": "Stres Ringan",
  "skor": 20,
  "explanation_trace": [...],
  "rekomendasi": [...]
}
```
