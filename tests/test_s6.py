import os, sys, tempfile, unittest
from pathlib import Path

TMP = tempfile.mkdtemp()
os.environ["S6_ROOT"] = TMP
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import s6  # noqa: E402


class T(unittest.TestCase):
    def setUp(self):
        s6.add_product("p1", "Manta eléctrica", "hogar", "estacional", "calor", 30, 40)

    def test_verified_needs_primary_source(self):
        with self.assertRaises(SystemExit):
            s6.add_evidence("p1", "x", "VERIFICADO", "secundario", "alta", "http://a", "a", "2026-10-01")

    def test_estimate_needs_source_and_date(self):
        with self.assertRaises(SystemExit):
            s6.add_evidence("p1", "x", "ESTIMACION", "secundario", "baja")

    def test_hypothesis_without_source_ok(self):
        self.assertEqual(s6.add_evidence("p1", "x", "HIPOTESIS", "secundario", "baja")["kind"], "HIPOTESIS")

    def test_economics(self):
        e = s6.economics(121, 20, 5, "ES", return_rate=0, pay_pct=0, pay_fixed=0)
        self.assertEqual(e["net"], 100.0)
        self.assertEqual(e["contribution_pre_ads"], 75.0)

    def test_unknown_country(self):
        with self.assertRaises(SystemExit):
            s6.economics(10, 1, 1, "ZZ")

    def test_combos_order_and_discard(self):
        s6.set_market("p1", "es", "alternativo", "r", "baja")
        s6.set_market("p1", "de", "recomendado", "r", "media")
        s6.set_costs("p1", 10, 4, "estimado")
        rows = s6.combos()
        self.assertEqual(rows[0]["country"], "DE")
        self.assertIsNotNone(rows[0]["breakeven_cpa"])

    def test_report_and_export(self):
        self.assertTrue(s6.report().exists())
        self.assertTrue((s6.export() / "combos.csv").exists())


if __name__ == "__main__":
    unittest.main()
