from .compat import patch_collections_compat

patch_collections_compat()

from experta import Fact, Field  # noqa: E402


class Gejala(Fact):
    """Fakta gejala yang dipilih pengguna, disimpan di working memory."""

    nama = Field(str, mandatory=True)


class Kondisi(Fact):
    """Fakta kesimpulan kondisi kesehatan mental hasil inferensi.

    Setiap kali sebuah aturan (rule) terpenuhi, aturan tersebut akan
    melakukan firing dan mendeklarasikan fact Kondisi baru berisi nama
    kondisi, skor keparahan, dan teks aturan IF-THEN yang aktif -- ini
    yang menjadi dasar explanation trace pada Heal.In.
    """

    nama = Field(str, mandatory=True)
    skor = Field(int, mandatory=True)
    aturan = Field(str, mandatory=True)
