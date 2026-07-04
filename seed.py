"""Script seeding data awal untuk database PostgreSQL Heal.In.

Mengisi tabel symptoms, conditions, rules (metadata), dan recommendations
berdasarkan data yang SUDAH ADA di rules/gejala_list.py dan
rules/rekomendasi.py, serta ringkasan aturan IF-THEN yang diimplementasikan
di rules/*_rules.py (Experta).

PENTING: script ini HANYA mengisi database (bacaan referensi, bukan
mesin inferensi). Rule engine Experta yang sesungguhnya (forward
chaining) tetap sepenuhnya berjalan dari kelas Rule di rules/*_rules.py
dan TIDAK diubah oleh script ini.

Jalankan setelah migrasi database selesai:
    python seed.py
"""
from api.app import app
from models import db
from models.models import Condition, Recommendation, Rule, Symptom
from rules.gejala_list import (
    GEJALA_FISIK,
    GEJALA_KOGNITIF,
    GEJALA_EMOSIONAL,
    GEJALA_PERILAKU,
)
from rules.rekomendasi import REKOMENDASI

# --------------------------------------------------------------------- #
# Master data gejala, dikelompokkan sesuai kategori di gejala_list.py
# --------------------------------------------------------------------- #
SYMPTOM_CATEGORIES = {
    "fisik": GEJALA_FISIK,
    "kognitif": GEJALA_KOGNITIF,
    "emosional": GEJALA_EMOSIONAL,
    "perilaku": GEJALA_PERILAKU,
}


def _humanize(code: str) -> str:
    """Ubah 'sulit_tidur' -> 'Sulit Tidur' untuk nama tampilan."""
    return code.replace("_", " ").title()


# --------------------------------------------------------------------- #
# Master data kondisi + ringkasan aturan per kondisi (selaras dengan
# salience & contoh aturan pada rules/*_rules.py dan proposal Bab 5).
# rule_code & explanation di sini adalah RINGKASAN untuk riwayat/dashboard,
# bukan pengganti kelas Rule Experta yang sesungguhnya menjalankan
# forward chaining.
# --------------------------------------------------------------------- #
CONDITIONS = [
    {
        "code": "normal",
        "condition_name": "Normal",
        "severity": "Rendah",
        "description": "Gejala yang dilaporkan sangat sedikit dan tidak "
        "mengarah ke stres, kecemasan, maupun depresi.",
        "priority": 5,
        "rules": [
            (
                "normal_1",
                "IF mudah_lelah AND NOT sulit_tidur AND NOT cemas_berlebihan "
                "AND NOT sedih_berkepanjangan THEN Normal",
            ),
            (
                "normal_2",
                "IF sakit_kepala AND NOT sulit_konsentrasi AND NOT "
                "cemas_berlebihan THEN Normal",
            ),
            (
                "normal_3",
                "IF mudah_lupa AND NOT sulit_konsentrasi AND NOT "
                "pikiran_negatif THEN Normal",
            ),
        ],
    },
    {
        "code": "stres_ringan",
        "condition_name": "Stres Ringan",
        "severity": "Ringan",
        "description": "Kombinasi 2-3 gejala ringan, umumnya dipicu "
        "tekanan akademik jangka pendek.",
        "priority": 20,
        "rules": [
            (
                "stres_ringan_1",
                "IF sulit_tidur AND cemas_berlebihan AND sulit_konsentrasi "
                "THEN Stres Ringan",
            ),
            (
                "stres_ringan_2",
                "IF sulit_tidur AND mudah_lelah THEN Stres Ringan",
            ),
            (
                "stres_ringan_3",
                "IF sakit_kepala AND sulit_konsentrasi THEN Stres Ringan",
            ),
            (
                "stres_ringan_4",
                "IF mudah_lelah AND penurunan_produktivitas THEN Stres Ringan",
            ),
            (
                "stres_ringan_5",
                "IF sulit_konsentrasi AND mudah_lupa THEN Stres Ringan",
            ),
        ],
    },
    {
        "code": "stres_berat",
        "condition_name": "Stres Berat",
        "severity": "Berat",
        "description": "Kombinasi 3-4 gejala lintas kategori (fisik, "
        "kognitif, emosional, perilaku) yang muncul bersamaan.",
        "priority": 40,
        "rules": [
            (
                "stres_berat_1",
                "IF sulit_tidur AND cemas_berlebihan AND sulit_konsentrasi "
                "AND kehilangan_motivasi THEN Stres Berat",
            ),
            (
                "stres_berat_2",
                "IF mudah_lelah AND sakit_kepala AND sulit_konsentrasi AND "
                "mudah_marah THEN Stres Berat",
            ),
            (
                "stres_berat_3",
                "IF sulit_tidur AND mudah_marah AND penurunan_produktivitas "
                "THEN Stres Berat",
            ),
            (
                "stres_berat_4",
                "IF pikiran_negatif AND sulit_konsentrasi AND mudah_lelah "
                "AND sulit_tidur THEN Stres Berat",
            ),
            (
                "stres_berat_5",
                "IF cemas_berlebihan AND mudah_marah AND sulit_tidur AND "
                "penurunan_produktivitas THEN Stres Berat",
            ),
        ],
    },
    {
        "code": "kecemasan",
        "condition_name": "Kecemasan",
        "severity": "Sedang-Berat",
        "description": "Berpusat pada gejala cemas_berlebihan yang "
        "dikombinasikan dengan gejala penyerta lain.",
        "priority": 30,
        "rules": [
            (
                "kecemasan_1",
                "IF cemas_berlebihan AND sulit_tidur AND mudah_marah THEN "
                "Kecemasan",
            ),
            (
                "kecemasan_2",
                "IF cemas_berlebihan AND sakit_kepala THEN Kecemasan",
            ),
            (
                "kecemasan_3",
                "IF cemas_berlebihan AND pikiran_negatif THEN Kecemasan",
            ),
            (
                "kecemasan_4",
                "IF cemas_berlebihan AND menarik_diri THEN Kecemasan",
            ),
            (
                "kecemasan_5",
                "IF cemas_berlebihan AND mudah_lupa AND sulit_konsentrasi "
                "THEN Kecemasan",
            ),
        ],
    },
    {
        "code": "potensi_depresi",
        "condition_name": "Potensi Depresi",
        "severity": "Tinggi",
        "description": "Prioritas tertinggi karena tingkat keparahan "
        "paling serius, berpusat pada gejala emosional "
        "(sedih_berkepanjangan, putus_asa) dan penarikan diri.",
        "priority": 50,
        "rules": [
            (
                "depresi_1",
                "IF sedih_berkepanjangan AND kehilangan_motivasi THEN "
                "Potensi Depresi",
            ),
            (
                "depresi_2",
                "IF putus_asa AND kehilangan_motivasi AND menarik_diri "
                "THEN Potensi Depresi",
            ),
            (
                "depresi_3",
                "IF sedih_berkepanjangan AND menarik_diri THEN Potensi "
                "Depresi",
            ),
            (
                "depresi_4",
                "IF putus_asa AND penurunan_produktivitas THEN Potensi "
                "Depresi",
            ),
            (
                "depresi_5",
                "IF sedih_berkepanjangan AND pikiran_negatif AND "
                "kehilangan_motivasi THEN Potensi Depresi",
            ),
            (
                "depresi_6",
                "IF putus_asa AND sedih_berkepanjangan THEN Potensi Depresi",
            ),
        ],
    },
]


def seed_symptoms():
    created = 0
    for category, codes in SYMPTOM_CATEGORIES.items():
        for code in codes:
            if Symptom.query.filter_by(code=code).first():
                continue
            db.session.add(
                Symptom(code=code, symptom_name=_humanize(code), category=category)
            )
            created += 1
    db.session.commit()
    print(f"[seed] symptoms: {created} baris baru ditambahkan.")


def seed_conditions_rules_recommendations():
    conditions_created = 0
    rules_created = 0
    recommendations_created = 0

    for item in CONDITIONS:
        condition = Condition.query.filter_by(code=item["code"]).first()
        if not condition:
            condition = Condition(
                code=item["code"],
                condition_name=item["condition_name"],
                severity=item["severity"],
                description=item["description"],
            )
            db.session.add(condition)
            db.session.flush()  # supaya condition.id tersedia utk FK
            conditions_created += 1

        for rule_code, explanation in item["rules"]:
            if Rule.query.filter_by(rule_code=rule_code).first():
                continue
            db.session.add(
                Rule(
                    rule_code=rule_code,
                    condition_id=condition.id,
                    priority=item["priority"],
                    explanation=explanation,
                )
            )
            rules_created += 1

        for recommendation_text in REKOMENDASI.get(item["condition_name"], []):
            exists = Recommendation.query.filter_by(
                condition_id=condition.id, recommendation=recommendation_text
            ).first()
            if exists:
                continue
            db.session.add(
                Recommendation(
                    condition_id=condition.id, recommendation=recommendation_text
                )
            )
            recommendations_created += 1

    db.session.commit()
    print(f"[seed] conditions: {conditions_created} baris baru ditambahkan.")
    print(f"[seed] rules: {rules_created} baris baru ditambahkan.")
    print(f"[seed] recommendations: {recommendations_created} baris baru ditambahkan.")


def main():
    with app.app_context():
        try:
            seed_symptoms()
            seed_conditions_rules_recommendations()
            print("[seed] Selesai. Database siap digunakan.")
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            print(
                "[seed] GAGAL melakukan seeding data. Pastikan PostgreSQL "
                "sudah menyala dan 'flask db upgrade' sudah dijalankan "
                f"terlebih dahulu. Detail error: {exc}"
            )
            raise


if __name__ == "__main__":
    main()
