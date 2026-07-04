"""Inisialisasi ekstensi database Heal.In.

`db` adalah instance Flask-SQLAlchemy tunggal yang dipakai bersama oleh
seluruh model (models.py) dan oleh Flask-Migrate (lihat api/app.py).
Dipisah ke sini supaya models.py dan app.py bisa sama-sama meng-import
`db` tanpa import melingkar (circular import).
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
