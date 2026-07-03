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

## Menjalankan

```bash
pip install -r requirements.txt

# Demo cepat lewat terminal
python demo.py

# Unit test
pytest test_engine.py -v

# Jalankan REST API (http://localhost:5000)
python api/app.py
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
