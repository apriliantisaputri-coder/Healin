"""
Demo baris perintah: mereplikasi skenario "Andi" pada proposal
(Bab 6e - Contoh Skenario Pengguna).

Jalankan: python demo.py
"""

from engine.knowledge_engine import run_inference
from rules.rekomendasi import get_rekomendasi

if __name__ == "__main__":
    gejala_andi = [
        "sulit_tidur",
        "cemas_berlebihan",
        "sulit_konsentrasi",
        "kehilangan_motivasi",
    ]

    hasil = run_inference(gejala_andi)

    print("=== Skrining Heal.In ===")
    print("Gejala yang dipilih :", ", ".join(gejala_andi))
    print("Kondisi terdeteksi  :", hasil["kondisi"], f"(skor {hasil['skor']})")
    print("\nExplanation trace (aturan yang aktif):")
    for i, jejak in enumerate(hasil["explanation_trace"], start=1):
        print(f"  {i}. [{jejak['kondisi']}] {jejak['aturan']}")

    print("\nRekomendasi tindak lanjut:")
    for saran in get_rekomendasi(hasil["kondisi"]):
        print(" -", saran)
