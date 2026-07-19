import json
import unittest

from datahub_roundtrip import build_receipt


class ReceiptSafetyTests(unittest.TestCase):
    def test_missing_or_invalid_freshness_fails_closed(self):
        for feature in ({"kind": "FeatureSet"}, {"kind": "FeatureSet", "freshness": "not-a-date"}):
            evidence = {
                "model": "m@1",
                "nodes": [feature, {"kind": "MLModel", "owner": "ml"}],
                "rollbackRunbook": "urn:li:document:rollback",
            }
            receipt = build_receipt(evidence, "2026-07-19")
            self.assertEqual(receipt["verdict"], "REPAIR")
            self.assertEqual([gap["id"] for gap in receipt["gaps"]], ["missing-freshness"])

    def test_missing_feature_node_fails_closed(self):
        evidence = {
            "model": "m@1",
            "nodes": [{"kind": "MLModel", "owner": "ml"}],
            "rollbackRunbook": "urn:li:document:rollback",
        }
        receipt = build_receipt(evidence, "2026-07-19")
        self.assertEqual([gap["id"] for gap in receipt["gaps"]], ["missing-freshness"])

    def test_committed_fixture_matches_python_engine(self):
        with open("evidence-datahub-roundtrip.json", encoding="utf-8") as handle:
            fixture = json.load(handle)
        self.assertEqual(build_receipt(fixture["evidence"], "2026-07-19"), fixture["receipt"])

    def test_receipt_digest_binds_the_evidence_snapshot(self):
        evidence = {
            "model": "m@1",
            "nodes": [{"kind": "FeatureSet", "name": "features", "owner": "data", "freshness": "2026-06-01"}, {"kind": "MLModel", "owner": None}],
            "rollbackRunbook": None,
        }
        changed = json.loads(json.dumps(evidence))
        changed["nodes"][0]["owner"] = "another-team"
        self.assertNotEqual(build_receipt(evidence, "2026-07-19")["digest"], build_receipt(changed, "2026-07-19")["digest"])


if __name__ == "__main__":
    unittest.main()
