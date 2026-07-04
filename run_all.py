"""Setup + jalankan Heal.In otomatis, SATU LANGKAH SAJA.

Script ini menggantikan seluruh urutan perintah manual:
    pip install -r requirements.txt
    (buat database healin_db lewat psql/pgAdmin)
    flask --app api.app db upgrade
    python seed.py
    python api/app.py

Aman dijalankan BERULANG KALI (idempoten): kalau database/tabel/data
sudah ada, langkah itu otomatis dilewati -- tidak akan menduplikasi
atau merusak data yang sudah tersimpan.

Cara pakai:
    python run_all.py
(atau cukup double-click start.bat di Windows / start.sh di Mac/Linux)

Prasyarat yang TETAP harus dilakukan manual (tidak bisa diotomatisasi
dengan aman): PostgreSQL sudah ter-install & service-nya menyala, dan
file .env sudah diisi DB_PASSWORD sesuai password PostgreSQL kamu.
"""
import os
import sys
import webbrowser
from threading import Timer

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "healin_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


def pastikan_database_ada():
    """Membuat database healin_db kalau belum ada, tanpa perlu psql/pgAdmin manual."""
    import psycopg2
    from psycopg2 import sql

    print(f"[1/4] Mengecek database '{DB_NAME}'...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
            dbname="postgres",  # koneksi ke database maintenance bawaan PostgreSQL
        )
    except Exception as exc:  # noqa: BLE001
        print(
            "\n[GAGAL] Tidak bisa terhubung ke PostgreSQL sama sekali.\n"
            "Kemungkinan penyebab:\n"
            "  - Service PostgreSQL belum menyala\n"
            "  - DB_PASSWORD di file .env salah\n"
            "  - DB_HOST/DB_PORT di .env tidak sesuai instalasi kamu\n"
            f"Detail error asli: {exc}\n"
        )
        sys.exit(1)

    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
            if cur.fetchone():
                print(f"      Database '{DB_NAME}' sudah ada, lanjut.")
            else:
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
                print(f"      Database '{DB_NAME}' berhasil dibuat.")
    finally:
        conn.close()


def jalankan_migrasi_dan_seed():
    # Import di sini (bukan di top-level) supaya pastikan_database_ada()
    # sempat jalan dulu -- import api.app langsung mencoba konek ke
    # healin_db, yang baru pasti ada setelah langkah di atas.
    from flask_migrate import upgrade
    from api.app import app

    print("[2/4] Menjalankan migrasi skema tabel...")
    with app.app_context():
        upgrade()
    print("      Migrasi selesai (atau sudah up-to-date).")

    print("[3/4] Mengisi data awal (gejala, kondisi, aturan, rekomendasi)...")
    import seed

    with app.app_context():
        seed.seed_symptoms()
        seed.seed_conditions_rules_recommendations()
    print("      Seed data selesai (atau sudah lengkap sebelumnya).")

    return app


def buka_browser():
    try:
        webbrowser.open("http://127.0.0.1:5000/")
    except Exception:  # noqa: BLE001
        pass


def main():
    pastikan_database_ada()
    app = jalankan_migrasi_dan_seed()

    print("[4/4] Menjalankan server Heal.In di http://127.0.0.1:5000 ...")
    print("      (biarkan jendela ini tetap terbuka selama memakai aplikasi)")
    print("      Tekan CTRL+C untuk berhenti.\n")

    Timer(1.5, buka_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
