from experta import Rule
from engine.facts import Gejala

SALIENCE_KECEMASAN = 30


class KecemasanRules:
    """Aturan untuk kondisi Kecemasan (Anxiety): berpusat pada gejala
    cemas_berlebihan yang dikombinasikan dengan gejala penyerta lain."""

    @Rule(
        Gejala(nama="cemas_berlebihan"),
        Gejala(nama="sulit_tidur"),
        Gejala(nama="mudah_marah"),
        salience=SALIENCE_KECEMASAN,
    )
    def kecemasan_1(self):
        self._catat(
            "Kecemasan",
            30,
            "IF cemas_berlebihan AND sulit_tidur AND mudah_marah THEN " "Kecemasan",
        )

    @Rule(
        Gejala(nama="cemas_berlebihan"),
        Gejala(nama="sakit_kepala"),
        salience=SALIENCE_KECEMASAN,
    )
    def kecemasan_2(self):
        self._catat("Kecemasan", 26, "IF cemas_berlebihan AND sakit_kepala THEN Kecemasan")

    @Rule(
        Gejala(nama="cemas_berlebihan"),
        Gejala(nama="pikiran_negatif"),
        salience=SALIENCE_KECEMASAN,
    )
    def kecemasan_3(self):
        self._catat(
            "Kecemasan",
            28,
            "IF cemas_berlebihan AND pikiran_negatif THEN Kecemasan",
        )

    @Rule(
        Gejala(nama="cemas_berlebihan"),
        Gejala(nama="menarik_diri"),
        salience=SALIENCE_KECEMASAN,
    )
    def kecemasan_4(self):
        self._catat("Kecemasan", 28, "IF cemas_berlebihan AND menarik_diri THEN Kecemasan")

    @Rule(
        Gejala(nama="cemas_berlebihan"),
        Gejala(nama="mudah_lupa"),
        Gejala(nama="sulit_konsentrasi"),
        salience=SALIENCE_KECEMASAN,
    )
    def kecemasan_5(self):
        self._catat(
            "Kecemasan",
            30,
            "IF cemas_berlebihan AND mudah_lupa AND sulit_konsentrasi THEN " "Kecemasan",
        )
