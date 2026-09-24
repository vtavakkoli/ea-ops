from pathlib import Path
import tempfile
import unittest

from eaops.core import load_repository, validate


class GovernanceAllowedValuesTests(unittest.TestCase):
    def test_allowed_property_values_are_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for folder in ("model", "relationships", "views", "rules"):
                (root / folder).mkdir()
            (root / "metamodel.yaml").write_text(
                """name: Test
elementTypes:
  ApplicationComponent: {layer: application}
relationshipTypes: {}
""",
                encoding="utf-8",
            )
            (root / "eaops.yaml").write_text(
                """name: Allowed Values
metamodel: {path: metamodel.yaml}
paths: {model: model, relationships: relationships, views: views, rules: rules}
""",
                encoding="utf-8",
            )
            (root / "model" / "model.yaml").write_text(
                """- id: app.test
  type: ApplicationComponent
  name: Test
  properties: {lifecycle: invalid}
""",
                encoding="utf-8",
            )
            (root / "rules" / "governance.yaml").write_text(
                """rules:
  - id: LIFECYCLE-001
    target: {type: ApplicationComponent}
    allow:
      properties:
        lifecycle: [active, strategic]
    severity: error
""",
                encoding="utf-8",
            )
            issues = validate(load_repository(root))
            self.assertTrue(any(i.code == "LIFECYCLE-001" and i.object_id == "app.test" for i in issues))


if __name__ == "__main__":
    unittest.main()
