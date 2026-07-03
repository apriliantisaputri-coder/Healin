"""Rekomendasi tindak lanjut sesuai tingkat keparahan kondisi
yang terdeteksi -- mulai dari saran pengelolaan mandiri hingga
anjuran konsultasi profesional (lihat proposal Heal.In Bab 6c)."""

REKOMENDASI = {
    "Normal": [
        "Pertahankan pola tidur dan aktivitas yang sudah baik.",
        "Lakukan jeda singkat di sela belajar agar tetap segar.",
    ],
    "Stres Ringan": [
        "Terapkan teknik manajemen waktu sederhana (mis. to-do list harian).",
        "Latihan pernapasan/relaksasi singkat sebelum tidur.",
        "Jaga pola tidur yang teratur.",
    ],
    "Stres Berat": [
        "Kurangi beban aktivitas yang menumpuk dan atur prioritas tugas.",
        "Coba teknik relaksasi terpandu atau olahraga ringan secara rutin.",
        "Pertimbangkan konsultasi dengan konselor kampus apabila gejala berlanjut.",
    ],
    "Kecemasan": [
        "Latihan pernapasan dalam (deep breathing) saat cemas muncul.",
        "Batasi paparan pemicu kecemasan yang berlebihan (mis. scrolling berita larut malam).",
        "Rujukan konsultasi ke konselor kampus disarankan.",
    ],
    "Potensi Depresi": [
        "Segera bicarakan kondisi ini dengan orang terdekat yang dipercaya.",
        "Sangat disarankan untuk berkonsultasi dengan psikolog atau tenaga medis profesional.",
        "Hindari mengambil keputusan besar sendirian saat kondisi belum stabil.",
    ],
}


def get_rekomendasi(nama_kondisi: str) -> list[str]:
    return REKOMENDASI.get(nama_kondisi, REKOMENDASI["Normal"])
