from experta import Rule
from engine.facts import Gejala

SALIENCE_DEPRESI = 50


class DepresiRules:
    """Aturan untuk kondisi Potensi Depresi: prioritas tertinggi karena
    tingkat keparahan paling serius, berpusat pada gejala emosional
    (sedih_berkepanjangan, putus_asa) dan perilaku penarikan diri."""

    @Rule(
        Gejala(nama="sedih_berkepanjangan"),
        Gejala(nama="kehilangan_motivasi"),
        salience=SALIENCE_DEPRESI,
    )
    def depresi_1(self):
        self._catat(
            "Potensi Depresi",
            48,
            "IF sedih_berkepanjangan AND kehilangan_motivasi THEN Potensi "
            "Depresi",
        )

    @Rule(
        Gejala(nama="putus_asa"),
        Gejala(nama="kehilangan_motivasi"),
        Gejala(nama="menarik_diri"),
        salience=SALIENCE_DEPRESI,
    )
    def depresi_2(self):
        self._catat(
            "Potensi Depresi",
            50,
            "IF putus_asa AND kehilangan_motivasi AND menarik_diri THEN "
            "Potensi Depresi",
        )

    @Rule(
        Gejala(nama="sedih_berkepanjangan"),
        Gejala(nama="menarik_diri"),
        salience=SALIENCE_DEPRESI,
    )
    def depresi_3(self):
        self._catat(
            "Potensi Depresi",
            46,
            "IF sedih_berkepanjangan AND menarik_diri THEN Potensi Depresi",
        )

    @Rule(
        Gejala(nama="putus_asa"),
        Gejala(nama="penurunan_produktivitas"),
        salience=SALIENCE_DEPRESI,
    )
    def depresi_4(self):
        self._catat(
            "Potensi Depresi",
            46,
            "IF putus_asa AND penurunan_produktivitas THEN Potensi Depresi",
        )

    @Rule(
        Gejala(nama="sedih_berkepanjangan"),
        Gejala(nama="pikiran_negatif"),
        Gejala(nama="kehilangan_motivasi"),
        salience=SALIENCE_DEPRESI,
    )
    def depresi_5(self):
        self._catat(
            "Potensi Depresi",
            50,
            "IF sedih_berkepanjangan AND pikiran_negatif AND "
            "kehilangan_motivasi THEN Potensi Depresi",
        )

    @Rule(
        Gejala(nama="putus_asa"),
        Gejala(nama="sedih_berkepanjangan"),
        salience=SALIENCE_DEPRESI,
    )
    def depresi_6(self):
        self._catat(
            "Potensi Depresi",
            50,
            "IF putus_asa AND sedih_berkepanjangan THEN Potensi Depresi",
        )
