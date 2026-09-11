from pathlib import Path
import unittest

from eaops.core import impact, load_repository, metrics, validate

ROOT = Path(__file__).parents[1] / "examples" / "sample-enterprise"


class CoreTests(unittest.TestCase):
    def test_sample_is_valid(self):
        repo = load_repository(ROOT)
        issues = validate(repo)
        self.assertFalse([x for x in issues if x.severity == "error"], issues)

    def test_metrics(self):
        repo = load_repository(ROOT)
        m = metrics(repo)
        self.assertGreaterEqual(m["objects"], 10)
        self.assertEqual(m["ownershipCoverage"], 100.0)

    def test_impact_traverses_graph(self):
        repo = load_repository(ROOT)
        result = impact(repo, {"app.crm"})
        self.assertIn("process.customer-onboarding", result["impacted"])
        self.assertIn("tech.api-gateway", result["impacted"])


if __name__ == "__main__":
    unittest.main()
