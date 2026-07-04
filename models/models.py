"""Skema database Heal.In menggunakan SQLAlchemy ORM (PostgreSQL).

Berisi dua kelompok model:

1. Model lama (Pengguna, SesiPemeriksaan) -- TETAP DIPERTAHANKAN persis
   seperti sebelumnya (nama tabel, kolom, relasi tidak diubah/dihapus).
   Satu-satunya perubahan adalah kelas dasarnya sekarang memakai
   `db.Model` (Flask-SQLAlchemy) alih-alih `declarative_base()` mandiri,
   supaya kedua kelompok model bisa dikenali dalam satu metadata yang
   sama oleh Flask-Migrate/Alembic saat migrasi ke PostgreSQL.

2. Model baru sesuai struktur database pada dokumen migrasi (users,
   symptoms, conditions, rules, recommendations, examination_history).
   Model-model ini menjadi fondasi untuk fitur Login, History, Dashboard,
   dan penyimpanan hasil skrining yang akan dibangun di atas database
   PostgreSQL, TANPA mengubah rule engine Experta maupun endpoint API
   yang sudah berjalan (/api/gejala, /api/skrining, /api/health).
"""
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Text,
)
from sqlalchemy.orm import relationship

from models import db

# ---------------------------------------------------------------------------
# Model lama (dipertahankan, tidak dihapus, tidak diubah struktur kolomnya)
# ---------------------------------------------------------------------------


class Pengguna(db.Model):
    __tablename__ = "pengguna"

    id = Column(Integer, primary_key=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    usia = Column(Integer, nullable=True)
    program_studi = Column(String(100), nullable=True)
    dibuat_pada = Column(DateTime, default=datetime.utcnow)

    sesi_pemeriksaan = relationship("SesiPemeriksaan", back_populates="pengguna")


class SesiPemeriksaan(db.Model):
    """Satu baris = satu kali sesi skrining yang dilakukan pengguna."""

    __tablename__ = "sesi_pemeriksaan"

    id = Column(Integer, primary_key=True)
    pengguna_id = Column(Integer, ForeignKey("pengguna.id"), nullable=False)
    gejala_dipilih = Column(JSON, nullable=False)  # list[str]
    kondisi_terdeteksi = Column(String(50), nullable=False)
    skor = Column(Integer, nullable=False)
    explanation_trace = Column(JSON, nullable=False)  # log aturan yang aktif
    rekomendasi = Column(JSON, nullable=False)
    tanggal_pemeriksaan = Column(DateTime, default=datetime.utcnow)

    pengguna = relationship("Pengguna", back_populates="sesi_pemeriksaan")


# ---------------------------------------------------------------------------
# Model baru -- fondasi PostgreSQL sesuai struktur database pada dokumen
# migrasi (users, symptoms, conditions, rules, recommendations,
# examination_history). Dipakai untuk fitur Login, History, Dashboard,
# dan penyimpanan hasil skrining ke depannya.
# ---------------------------------------------------------------------------


class User(db.Model):
    """Akun pengguna terautentikasi (fondasi fitur Login/Dashboard)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    age = Column(Integer, nullable=True)
    study_program = Column(String(150), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    examination_history = relationship(
        "ExaminationHistory", back_populates="user", cascade="all, delete-orphan"
    )


class Symptom(db.Model):
    """Master data gejala (fisik/kognitif/emosional/perilaku).

    Selaras dengan daftar gejala pada rules/gejala_list.py -- tabel ini
    hanya menyimpan datanya, TIDAK menggantikan atau mengubah cara
    rule engine Experta bekerja.
    """

    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True)
    code = Column(String(60), unique=True, nullable=False, index=True)
    symptom_name = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)  # fisik/kognitif/emosional/perilaku


class Condition(db.Model):
    """Master data kondisi kesehatan mental hasil identifikasi sistem."""

    __tablename__ = "conditions"

    id = Column(Integer, primary_key=True)
    code = Column(String(60), unique=True, nullable=False, index=True)
    condition_name = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)

    rules = relationship(
        "Rule", back_populates="condition", cascade="all, delete-orphan"
    )
    recommendations = relationship(
        "Recommendation", back_populates="condition", cascade="all, delete-orphan"
    )


class Rule(db.Model):
    """Metadata aturan IF-THEN (untuk pencatatan/riwayat, BUKAN mesin
    inferensi -- logika forward chaining tetap sepenuhnya berada di
    engine/knowledge_engine.py dan rules/*_rules.py memakai Experta)."""

    __tablename__ = "rules"

    id = Column(Integer, primary_key=True)
    rule_code = Column(String(60), unique=True, nullable=False, index=True)
    condition_id = Column(Integer, ForeignKey("conditions.id"), nullable=False)
    priority = Column(Integer, nullable=False)  # selaras dgn salience Experta
    explanation = Column(Text, nullable=False)  # teks aturan IF-THEN

    condition = relationship("Condition", back_populates="rules")


class Recommendation(db.Model):
    """Rekomendasi tindak lanjut per kondisi (selaras rules/rekomendasi.py)."""

    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)
    condition_id = Column(Integer, ForeignKey("conditions.id"), nullable=False)
    recommendation = Column(Text, nullable=False)

    condition = relationship("Condition", back_populates="recommendations")


class ExaminationHistory(db.Model):
    """Riwayat sesi pemeriksaan/skrining pengguna (fondasi fitur History)."""

    __tablename__ = "examination_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    examination_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    detected_condition = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=True)
    selected_symptoms = Column(JSON, nullable=False)  # list[str]
    explanation_trace = Column(JSON, nullable=False)  # list[str]
    recommendation = Column(JSON, nullable=False)  # list[str]
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="examination_history")
