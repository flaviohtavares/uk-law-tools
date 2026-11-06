"""Run with: python3 -m unittest discover tests"""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/uk-law/skills/uk-law/scripts"))
import uk_law  # noqa: E402

INDEX = """id,type,year,number,title,status,extent,topics,path
ukpga/2018/12,ukpga,2018,12,Data Protection Act 2018,revised,E+W+S+N.I.,Data Protection,uk-parliament/acts/public/2018/12-dpa/README.md
ukpga/1984/35,ukpga,1984,35,Data Protection Act 1984,repealed,E+W+S+N.I.,,uk-parliament/acts/public/1984/35-dpa.md
uksi/2019/419,uksi,2019,419,The Data Protection (Amendments etc) Regulations 2019,as-enacted,,Data Protection,uk-parliament/regulations/2019/0000-0499/419-dp.md
asp/2016/19,asp,2016,19,Private Housing (Tenancies) (Scotland) Act 2016,revised,S,Landlord and Tenant,scotland/acts/2016/19-pht.md
"""
README = """---
title: Data Protection Act 2018
---

## Contents

- [Section 1 — Overview](part-1/section-1.md)
- [Section 5 — Definitions](part-2/section-5.md)
- [SCHEDULE 1](schedule-1.md)
"""
TOPICS = """# Topics

| topic | Acts | regulations |
|---|---|---|
| [Data Protection](data-protection.md) | 1 | 1 |
| [Landlord and Tenant](landlord-and-tenant.md) | 1 | 0 |
"""


class UkLawTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        files = {"index/laws.csv": INDEX, "uk-parliament/acts/public/2018/12-dpa/README.md": README,
                 "uk-parliament/acts/public/2018/12-dpa/part-2/section-5.md": "# section 5 text",
                 "uk-parliament/acts/public/2018/12-dpa/schedule-1.md": "# schedule 1 text",
                 "topics/README.md": TOPICS, "topics/landlord-and-tenant.md": "# Landlord and Tenant page"}
        for rel, text in files.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text, encoding="utf-8")
        self.root = root

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = uk_law.main(["--repo", str(self.root), *args])
        return code, out.getvalue()

    def test_find_ranks_exact_title_acts_and_in_force_first(self):
        rows = uk_law.Source(str(self.root)).index()
        ids = [r["id"] for r in uk_law.search(rows, "data protection act")]
        self.assertEqual(ids, ["ukpga/2018/12", "ukpga/1984/35"])
        ids = [r["id"] for r in uk_law.search(rows, "data protection")]
        self.assertEqual(ids[0], "ukpga/2018/12")
        self.assertEqual([r["id"] for r in uk_law.search(rows, "data protection", in_force=True, types=["uksi"])],
                         ["uksi/2019/419"])
        self.assertNotIn("asp/2016/19", [r["id"] for r in uk_law.search(rows, "act", extent="W")])
        self.assertIn("asp/2016/19", [r["id"] for r in uk_law.search(rows, "act", extent="S")])
        self.assertEqual([r["id"] for r in uk_law.search(rows, "UKPGA/1984/35")], ["ukpga/1984/35"])

    def test_show_resolves_sections_and_schedules(self):
        self.assertIn("section 5 text", self.run_cli("show", "ukpga/2018/12", "section 5")[1])
        self.assertIn("section 5 text", self.run_cli("show", "ukpga/2018/12", "s.5")[1])
        self.assertIn("schedule 1 text", self.run_cli("show", "ukpga/2018/12", "sch 1")[1])
        code, out = self.run_cli("show", "ukpga/2018/12")
        self.assertIn("## Contents", out)
        self.assertIn("https://www.legislation.gov.uk/ukpga/2018/12", out)
        code, out = self.run_cli("show", "ukpga/2018/12", "part 2")
        self.assertIn("section-5", out)

    def test_topics(self):
        self.assertIn("Landlord and Tenant  (1 Acts, 0 regulations in force)", self.run_cli("topics", "tenant")[1])
        self.assertIn("Landlord and Tenant page", self.run_cli("topic", "landlord", "and", "tenant")[1])


if __name__ == "__main__":
    unittest.main()
