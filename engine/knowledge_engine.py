from .compat import patch_collections_compat

patch_collections_compat()

from experta import KnowledgeEngine  # noqa: E402

from engine.facts import Gejala, Kondisi  # noqa: E402
from rules.normal_rules import NormalRules  # noqa: E402
from rules.stres_ringan_rules import StresRinganRules  # noqa: E402
from rules.stres_berat_rules import StresBeratRules  # noqa: E402
from rules.kecemasan_rules import KecemasanRules  # noqa: E402
from rules.depresi_rules import DepresiRules  # noqa: E402


class HealInEngine(
    KnowledgeEngine,
    DepresiRules,
    StresBeratRules,
    KecemasanRules,
    StresRinganRules,
    NormalRules,
):
    """Mesin inferensi Forward Chaining untuk sistem pakar Heal.In.

    Alur kerja (lihat pseudocode pada Bab III laporan):
        1. Terima gejala pengguna -> declare sebagai Fact Gejala.
        2. engine.run() melakukan pattern matching & firing aturan
           IF-THEN secara berulang (ditangani otomatis oleh Experta).
        3. Setiap aturan yang aktif dicatat ke ``explanation_trace``.
        4. ``hasil_akhir()`` memilih kondisi dengan skor tertinggi
           sebagai kesimpulan (conflict resolution).
    """

    def __init__(self):
        super().__init__()
        self.explanation_trace = []

    def _catat(self, nama_kondisi: str, skor: int, aturan: str) -> None:
        """Dipanggil oleh setiap rule saat firing (eksekusi aturan).
        Menyimpan kesimpulan sebagai Fact baru & mencatat alur penalaran."""
        self.declare(Kondisi(nama=nama_kondisi, skor=skor, aturan=aturan))
        self.explanation_trace.append({"kondisi": nama_kondisi, "skor": skor, "aturan": aturan})

    def hasil_akhir(self) -> dict:
        """Menentukan kondisi akhir berdasarkan skor/prioritas tertinggi
        di antara seluruh aturan yang aktif (conflict resolution).

        Catatan implementasi (menjawab Bab 2.3.3/3.3 laporan): seluruh
        aturan yang kondisinya terpenuhi TETAP dieksekusi (Experta tidak
        dihentikan paksa setelah satu firing), dan setiap firing dicatat
        ke ``explanation_trace`` apa adanya. Nilai ``salience`` pada
        setiap ``@Rule`` (lihat SALIENCE_* di rules/*.py) hanya
        memengaruhi urutan eksekusi di agenda Experta.

        Konflik resolusi yang menentukan KESIMPULAN AKHIR dilakukan di
        sini dengan memilih fact ``Kondisi`` berskor tertinggi. Nilai
        ``skor`` pada tiap rule sengaja dikalibrasi agar rentangnya
        SELALU sejalan dengan urutan salience per kategori kondisi
        (Normal < Stres Ringan < Kecemasan < Stres Berat < Potensi
        Depresi; lihat konstanta SALIENCE_* pada rules/*_rules.py),
        sehingga secara efektif memprioritaskan kondisi dengan tingkat
        keparahan lebih tinggi -- persis seperti yang dideskripsikan
        pada laporan -- walau secara teknis pemilihannya lewat skor,
        bukan lewat menghentikan agenda Experta di rule bersalience
        tertinggi.
        """
        kondisi_aktif = [f for f in self.facts.values() if isinstance(f, Kondisi)]

        if not kondisi_aktif:
            return {
                "kondisi": "Normal",
                "skor": 0,
                "explanation_trace": [
                    {
                        "kondisi": "Normal",
                        "skor": 0,
                        "aturan": "Tidak ada aturan yang aktif -> default kondisi Normal",
                    }
                ],
            }

        terbaik = max(kondisi_aktif, key=lambda f: f["skor"])
        return {
            "kondisi": terbaik["nama"],
            "skor": terbaik["skor"],
            "explanation_trace": self.explanation_trace,
        }


def run_inference(daftar_gejala: list[str]) -> dict:
    """Fungsi bantu: jalankan satu sesi inferensi lengkap dari daftar
    nama gejala (list[str]) dan kembalikan hasil akhir + explanation trace."""
    engine = HealInEngine()
    engine.reset()
    for nama_gejala in daftar_gejala:
        engine.declare(Gejala(nama=nama_gejala))
    engine.run()
    return engine.hasil_akhir()
