"""
Unit test rule engine Heal.In, mengikuti Rencana Pengujian pada
proposal Bab 7E (Unit Testing pada Rule Engine).

Jalankan: pytest test_engine.py -v
"""
from engine.knowledge_engine import run_inference


def test_gejala_tunggal_normal():
    """Gejala tunggal ringan tanpa gejala penyerta -> Normal."""
    hasil = run_inference(["mudah_lelah"])
    assert hasil["kondisi"] == "Normal"


def test_stres_ringan_sesuai_contoh_proposal():
    """IF sulit_tidur AND cemas_berlebihan AND sulit_konsentrasi
    THEN Stres Ringan (contoh aturan pada proposal Bab 5a)."""
    hasil = run_inference(["sulit_tidur", "cemas_berlebihan", "sulit_konsentrasi"])
    assert hasil["kondisi"] == "Stres Ringan"
    assert any("Stres Ringan" in j["kondisi"] for j in hasil["explanation_trace"])


def test_potensi_depresi_sesuai_contoh_proposal():
    """IF merasa_putus_asa AND kehilangan_motivasi AND menarik_diri
    THEN Potensi Depresi (contoh aturan pada proposal Bab 5b)."""
    hasil = run_inference(["putus_asa", "kehilangan_motivasi", "menarik_diri"])
    assert hasil["kondisi"] == "Potensi Depresi"


def test_gejala_memenuhi_lebih_dari_satu_aturan_pilih_skor_tertinggi():
    """Gejala Andi pada skenario proposal (Bab 6e): memicu aturan Stres
    Ringan sekaligus mengarah ke Stres Berat -> sistem memilih kondisi
    dengan skor tertinggi di antara aturan yang aktif."""
    gejala = ["sulit_tidur", "cemas_berlebihan", "sulit_konsentrasi", "kehilangan_motivasi"]
    hasil = run_inference(gejala)
    assert hasil["kondisi"] == "Stres Berat"
    assert hasil["skor"] == max(j["skor"] for j in hasil["explanation_trace"])


def test_forward_chaining_berantai_ke_kondisi_paling_serius():
    """Fakta yang memicu beberapa kategori aturan sekaligus -> hasil
    akhir mengikuti kondisi dengan prioritas/skor tertinggi (Potensi
    Depresi > Stres Berat > Kecemasan > Stres Ringan > Normal)."""
    gejala = ["putus_asa", "sedih_berkepanjangan", "sulit_tidur", "mudah_lelah"]
    hasil = run_inference(gejala)
    assert hasil["kondisi"] == "Potensi Depresi"


def test_gejala_tidak_memenuhi_aturan_manapun():
    hasil = run_inference(["sulit_tidur"])
    assert hasil["kondisi"] == "Normal"
