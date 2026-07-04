from experta import Rule, NOT
from engine.facts import Gejala

SALIENCE_NORMAL = 5


class NormalRules:
    """Aturan untuk kondisi Normal: gejala yang dilaporkan sangat sedikit
    dan tidak mengarah ke kategori stres/kecemasan/depresi."""

    @Rule(
        Gejala(nama="mudah_lelah"),
        NOT(Gejala(nama="sulit_tidur")),
        NOT(Gejala(nama="cemas_berlebihan")),
        NOT(Gejala(nama="sedih_berkepanjangan")),
        salience=SALIENCE_NORMAL,
    )
    def normal_1(self):
        self._catat(
            "Normal",
            5,
            "IF mudah_lelah AND NOT sulit_tidur AND NOT cemas_berlebihan "
            "AND NOT sedih_berkepanjangan THEN Normal",
        )

    @Rule(
        Gejala(nama="sakit_kepala"),
        NOT(Gejala(nama="sulit_konsentrasi")),
        NOT(Gejala(nama="cemas_berlebihan")),
        salience=SALIENCE_NORMAL,
    )
    def normal_2(self):
        self._catat(
            "Normal",
            5,
            "IF sakit_kepala AND NOT sulit_konsentrasi AND NOT " "cemas_berlebihan THEN Normal",
        )

    @Rule(
        Gejala(nama="mudah_lupa"),
        NOT(Gejala(nama="sulit_konsentrasi")),
        NOT(Gejala(nama="pikiran_negatif")),
        salience=SALIENCE_NORMAL,
    )
    def normal_3(self):
        self._catat(
            "Normal",
            5,
            "IF mudah_lupa AND NOT sulit_konsentrasi AND NOT " "pikiran_negatif THEN Normal",
        )
