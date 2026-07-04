"""
Unit test murni untuk utilitas autentikasi Heal.In (api/auth_utils.py).

Sengaja TIDAK menyentuh Flask app / database (lihat test_auth_api.py
untuk pengujian endpoint end-to-end yang butuh koneksi PostgreSQL),
supaya test ini bisa langsung dijalankan di mesin mana pun tanpa
konfigurasi database, sama seperti semangat test_engine.py yang sudah
ada.

Jalankan: pytest test_auth_utils.py -v
"""

from datetime import datetime, timedelta

from api.auth_utils import hash_password, issue_token, verify_password


def test_password_hash_tidak_sama_dengan_plain_text():
    """Password yang di-hash tidak boleh identik dengan teks aslinya --
    ini yang membedakan implementasi baru dari sistem lama yang
    menyimpan password polos di localStorage."""
    hashed = hash_password("rahasia123")
    assert hashed != "rahasia123"
    assert len(hashed) > 20


def test_verify_password_benar():
    hashed = hash_password("sandiAman!")
    assert verify_password("sandiAman!", hashed) is True


def test_verify_password_salah():
    hashed = hash_password("sandiAman!")
    assert verify_password("sandiSalah!", hashed) is False


def test_issue_token_menghasilkan_token_unik_dan_masa_berlaku():
    token_a, expires_a = issue_token()
    token_b, _ = issue_token()

    assert token_a != token_b, "Setiap token sesi harus unik per penerbitan"
    assert len(token_a) > 20
    # Token harus kedaluwarsa di masa depan, tapi tidak lebih dari 24 jam
    # ke depan (sesuai TOKEN_LIFETIME=12 jam pada auth_utils.py).
    assert expires_a > datetime.utcnow()
    assert expires_a < datetime.utcnow() + timedelta(hours=24)
