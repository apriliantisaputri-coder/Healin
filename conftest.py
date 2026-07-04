"""
Konfigurasi pytest tingkat proyek.

Menetapkan DATABASE_URL ke SQLite in-memory SEBELUM modul mana pun
(termasuk api.app / config.py) diimpor oleh test, supaya seluruh test
yang butuh Flask app + database (mis. test_auth_api.py) bisa berjalan
tanpa perlu menyalakan server PostgreSQL sungguhan terlebih dahulu.

Ini TIDAK memengaruhi environment saat aplikasi dijalankan normal
(`python api/app.py` / `flask --app api.app run`), karena variabel ini
hanya berlaku selama proses pytest berjalan (dan hanya dipakai apabila
`DATABASE_URL`/kredensial PostgreSQL belum diset lewat .env sungguhan).
"""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
