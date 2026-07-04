from experta import Rule
from engine.facts import Gejala

SALIENCE_STRES_RINGAN = 20


class StresRinganRules:
    """Aturan untuk kondisi Stres Ringan: kombinasi 2-3 gejala ringan,
    umumnya dipicu tekanan akademik jangka pendek."""

    @Rule(
        Gejala(nama="sulit_tidur"),
        Gejala(nama="cemas_berlebihan"),
        Gejala(nama="sulit_konsentrasi"),
        salience=SALIENCE_STRES_RINGAN,
    )
    def stres_ringan_1(self):
        self._catat(
            "Stres Ringan",
            20,
            "IF sulit_tidur AND cemas_berlebihan AND sulit_konsentrasi " "THEN Stres Ringan",
        )

    @Rule(
        Gejala(nama="sulit_tidur"),
        Gejala(nama="mudah_lelah"),
        salience=SALIENCE_STRES_RINGAN,
    )
    def stres_ringan_2(self):
        self._catat("Stres Ringan", 18, "IF sulit_tidur AND mudah_lelah THEN Stres Ringan")

    @Rule(
        Gejala(nama="sakit_kepala"),
        Gejala(nama="sulit_konsentrasi"),
        salience=SALIENCE_STRES_RINGAN,
    )
    def stres_ringan_3(self):
        self._catat(
            "Stres Ringan",
            18,
            "IF sakit_kepala AND sulit_konsentrasi THEN Stres Ringan",
        )

    @Rule(
        Gejala(nama="mudah_lelah"),
        Gejala(nama="penurunan_produktivitas"),
        salience=SALIENCE_STRES_RINGAN,
    )
    def stres_ringan_4(self):
        self._catat(
            "Stres Ringan",
            18,
            "IF mudah_lelah AND penurunan_produktivitas THEN Stres Ringan",
        )

    @Rule(
        Gejala(nama="sulit_konsentrasi"),
        Gejala(nama="mudah_lupa"),
        salience=SALIENCE_STRES_RINGAN,
    )
    def stres_ringan_5(self):
        self._catat(
            "Stres Ringan",
            18,
            "IF sulit_konsentrasi AND mudah_lupa THEN Stres Ringan",
        )
