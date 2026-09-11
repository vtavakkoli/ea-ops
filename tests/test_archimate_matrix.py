from pathlib import Path
import hashlib
import os
import tempfile
import unittest

from eaops.archimate_matrix import _load_cached, parse_relationship_matrix
from eaops.core import load_repository, validate


MATRIX = b'''<?xml version="1.0" encoding="UTF-8"?>
<relationships version="3.2">
  <source concept="BusinessRole">
    <target concept="BusinessProcess" relations="io" />
  </source>
  <source concept="Stakeholder">
    <target concept="Driver" relations="no" />
  </source>
  <source concept="Relationship">
    <target concept="Goal" relations="o" />
  </source>
</relationships>
'''


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


class ArchimateMatrixTests(unittest.TestCase):
    def test_parser_expands_relation_codes(self):
        version, matrix = parse_relationship_matrix(MATRIX)
        self.assertEqual("3.2", version)
        self.assertEqual(frozenset({"Assignment", "Association"}), matrix[("BusinessRole", "BusinessProcess")])
        self.assertEqual(frozenset({"Influence", "Association"}), matrix[("Stakeholder", "Driver")])

    def test_validator_uses_exact_matrix_and_relationship_endpoints(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for folder in ("model", "relationships", "views", "rules"):
                (root / folder).mkdir()
            matrix_path = root / "matrix.xml"
            matrix_path.write_bytes(MATRIX)
            (root / "metamodel.yaml").write_text(
                f'''name: Test ArchiMate\nstandard: ArchiMate 3.2\nrelationshipMatrix:\n  version: "3.2"\n  required: true\n  gitBlobSha: "{git_blob_sha(MATRIX)}"\n  url: ""\nelementTypes:\n  BusinessRole: {{layer: business}}\n  BusinessProcess: {{layer: business}}\n  Stakeholder: {{layer: motivation}}\n  Driver: {{layer: motivation}}\n  Goal: {{layer: motivation}}\nrelationshipTypes:\n  Assignment: {{sourceTypes: ["*"], targetTypes: ["*"]}}\n  Influence: {{sourceTypes: ["*"], targetTypes: ["*"]}}\n  Association: {{sourceTypes: ["*"], targetTypes: ["*"]}}\n''',
                encoding="utf-8",
            )
            (root / "eaops.yaml").write_text(
                '''name: Matrix Test\nmetamodel:\n  path: metamodel.yaml\npaths:\n  model: model\n  relationships: relationships\n  views: views\n  rules: rules\n''',
                encoding="utf-8",
            )
            (root / "model" / "model.yaml").write_text(
                '''- {id: role.agent, type: BusinessRole, name: Agent}\n- {id: process.handle, type: BusinessProcess, name: Handle}\n- {id: stakeholder.user, type: Stakeholder, name: User}\n- {id: driver.digital, type: Driver, name: Digital}\n- {id: goal.fast, type: Goal, name: Fast}\n''',
                encoding="utf-8",
            )
            (root / "relationships" / "rels.yaml").write_text(
                '''- {id: rel.valid, type: Assignment, source: role.agent, target: process.handle}\n- {id: rel.invalid, type: Assignment, source: stakeholder.user, target: driver.digital}\n- {id: rel.to-relationship, type: Association, source: rel.valid, target: goal.fast}\n''',
                encoding="utf-8",
            )
            old = os.environ.get("EAOPS_ARCHIMATE_MATRIX")
            os.environ["EAOPS_ARCHIMATE_MATRIX"] = str(matrix_path)
            _load_cached.cache_clear()
            try:
                issues = validate(load_repository(root))
            finally:
                _load_cached.cache_clear()
                if old is None:
                    os.environ.pop("EAOPS_ARCHIMATE_MATRIX", None)
                else:
                    os.environ["EAOPS_ARCHIMATE_MATRIX"] = old
            invalid = [i for i in issues if i.code == "INVALID_RELATIONSHIP"]
            self.assertEqual(1, len(invalid))
            self.assertEqual("rel.invalid", invalid[0].object_id)
            self.assertIn("Allowed: Association, Influence", invalid[0].message)


if __name__ == "__main__":
    unittest.main()
