"""Konfigurasi aplikasi Heal.In.

Seluruh konfigurasi database dibaca dari environment variable (lihat
`.env.example`) -- TIDAK ADA password yang di-hardcode di source code,
sesuai ketentuan migrasi ke PostgreSQL.

Prioritas pembentukan URI database:
1. Jika `DATABASE_URL` sudah diset langsung, pakai itu.
2. Jika tidak, bentuk otomatis dari DB_HOST/DB_PORT/DB_NAME/DB_USER/
   DB_PASSWORD.
"""

import os

from dotenv import load_dotenv

# Muat variabel dari file .env (jika ada) ke environment sebelum dibaca.
load_dotenv()


def _build_database_url() -> str:
    """Membentuk connection string PostgreSQL dari environment variable."""
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url

    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "healin_db")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


class Config:
    """Konfigurasi utama Flask (dipakai di api/app.py)."""

    SQLALCHEMY_DATABASE_URI = _build_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        # pool_pre_ping mencegah error koneksi "stale" ke PostgreSQL
        # yang sempat idle terlalu lama.
        "pool_pre_ping": True,
    }

    # Dipakai untuk pesan error yang lebih jelas apabila koneksi gagal.
    DATABASE_NAME_FOR_LOG = os.getenv("DB_NAME", "healin_db")
