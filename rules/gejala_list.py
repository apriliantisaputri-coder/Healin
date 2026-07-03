"""
Daftar seluruh gejala yang dikenali sistem Heal.In, dikelompokkan
sesuai kategori pada proposal: fisik, kognitif, emosional, perilaku.
Digunakan untuk validasi input pada endpoint API dan untuk membangun
formulir checklist pada frontend.
"""

GEJALA_FISIK = [
    "sulit_tidur",
    "mudah_lelah",
    "sakit_kepala",
]

GEJALA_KOGNITIF = [
    "sulit_konsentrasi",
    "mudah_lupa",
    "pikiran_negatif",
]

GEJALA_EMOSIONAL = [
    "cemas_berlebihan",
    "mudah_marah",
    "sedih_berkepanjangan",
    "putus_asa",
]

GEJALA_PERILAKU = [
    "kehilangan_motivasi",
    "menarik_diri",
    "penurunan_produktivitas",
]

SEMUA_GEJALA = set(GEJALA_FISIK + GEJALA_KOGNITIF + GEJALA_EMOSIONAL + GEJALA_PERILAKU)
