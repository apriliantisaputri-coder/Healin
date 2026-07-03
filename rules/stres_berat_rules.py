from experta import Rule
from engine.facts import Gejala

SALIENCE_STRES_BERAT = 40


class StresBeratRules:
    """Aturan untuk kondisi Stres Berat: kombinasi 3-4 gejala lintas
    kategori (fisik, kognitif, emosional, perilaku) yang muncul bersamaan."""

    @Rule(
        Gejala(nama="sulit_tidur"),
        Gejala(nama="cemas_berlebihan"),
        Gejala(nama="sulit_konsentrasi"),
        Gejala(nama="kehilangan_motivasi"),
        salience=SALIENCE_STRES_BERAT,
    )
    def stres_berat_1(self):
        self._catat(
            "Stres Berat",
            40,
            "IF sulit_tidur AND cemas_berlebihan AND sulit_konsentrasi "
            "AND kehilangan_motivasi THEN Stres Berat",
        )

    @Rule(
        Gejala(nama="mudah_lelah"),
        Gejala(nama="sakit_kepala"),
        Gejala(nama="sulit_konsentrasi"),
        Gejala(nama="mudah_marah"),
        salience=SALIENCE_STRES_BERAT,
    )
    def stres_berat_2(self):
        self._catat(
            "Stres Berat",
            38,
            "IF mudah_lelah AND sakit_kepala AND sulit_konsentrasi AND "
            "mudah_marah THEN Stres Berat",
        )

    @Rule(
        Gejala(nama="sulit_tidur"),
        Gejala(nama="mudah_marah"),
        Gejala(nama="penurunan_produktivitas"),
        salience=SALIENCE_STRES_BERAT,
    )
    def stres_berat_3(self):
        self._catat(
            "Stres Berat",
            36,
            "IF sulit_tidur AND mudah_marah AND penurunan_produktivitas "
            "THEN Stres Berat",
        )

    @Rule(
        Gejala(nama="pikiran_negatif"),
        Gejala(nama="sulit_konsentrasi"),
        Gejala(nama="mudah_lelah"),
        Gejala(nama="sulit_tidur"),
        salience=SALIENCE_STRES_BERAT,
    )
    def stres_berat_4(self):
        self._catat(
            "Stres Berat",
            38,
            "IF pikiran_negatif AND sulit_konsentrasi AND mudah_lelah AND "
            "sulit_tidur THEN Stres Berat",
        )

    @Rule(
        Gejala(nama="cemas_berlebihan"),
        Gejala(nama="mudah_marah"),
        Gejala(nama="sulit_tidur"),
        Gejala(nama="penurunan_produktivitas"),
        salience=SALIENCE_STRES_BERAT,
    )
    def stres_berat_5(self):
        self._catat(
            "Stres Berat",
            40,
            "IF cemas_berlebihan AND mudah_marah AND sulit_tidur AND "
            "penurunan_produktivitas THEN Stres Berat",
        )
