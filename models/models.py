"""Skema database Heal.In menggunakan SQLAlchemy ORM (PostgreSQL).

Menyimpan data pengguna dan riwayat sesi pemeriksaan sesuai rancangan
pada proposal Bab 6d (Lapisan Data)."""
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Pengguna(Base):
    __tablename__ = "pengguna"

    id = Column(Integer, primary_key=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    usia = Column(Integer, nullable=True)
    program_studi = Column(String(100), nullable=True)
    dibuat_pada = Column(DateTime, default=datetime.utcnow)

    sesi_pemeriksaan = relationship("SesiPemeriksaan", back_populates="pengguna")


class SesiPemeriksaan(Base):
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
