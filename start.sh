#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "============================================"
echo "  Heal.In - Setup & Jalankan Otomatis"
echo "============================================"
echo

if [ ! -f ".env" ]; then
  echo "[PENTING] File .env belum ada. Menyalin dari .env.example..."
  cp .env.example .env
  echo
  echo "Silakan buka file .env, isi DB_PASSWORD sesuai password"
  echo "PostgreSQL kamu, simpan, lalu jalankan ulang ./start.sh ini."
  exit 1
fi

echo "Mengecek/menginstall dependency Python..."
pip install -r requirements.txt

echo
echo "Menyiapkan database, migrasi, dan seed data..."
python3 run_all.py
