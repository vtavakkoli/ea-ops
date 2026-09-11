from pathlib import Path
import tempfile
import unittest

from eaops.core import load_repository, validate
from eaops.portal import render_portal


class PortalTests(unittest.TestCase):
    def _repository(self, root: Path):
        (root / "model").mkdir()
        (root / "relationships").mkdir()
        (root / "views").mkdir()
        (root / "rules").mkdir()
        (root / "eaops.yaml").write_text(
            """name: Portal Test\nmetamodel:\n  builtin: archimate-3.2\npaths:\n  model: model\n  relationships: relationships\n  views: views\n  rules: rules\n""",
            encoding="utf-8",
        )
        (root / "model" / "business.yaml").write_text(
            """- id: event.message\n  type: BusinessEvent\n  name: Request Received\n  description: Incoming request event.\n  properties: {owner: Service, eventKind: message}\n- id: process.handle\n  type: BusinessProcess\n  name: Handle Request\n  description: Handle the incoming request.\n  properties: {owner: Service, criticality: high}\n- id: object.request\n  type: BusinessObject\n  name: Request\n  description: Business information object.\n  properties: {owner: Service}\n- id: representation.request-pdf\n  type: Representation\n  name: Request PDF\n  description: Human-readable representation.\n  properties: {owner: Service, format: PDF}\n""",
            encoding="utf-8",
        )
        (root / "relationships" / "relationships.yaml").write_text(
            """- {id: rel.event-process, type: Triggering, source: event.message, target: process.handle}\n- {id: rel.process-doc, type: Access, source: process.handle, target: representation.request-pdf}\n- {id: rel.doc-object, type: Realization, source: representation.request-pdf, target: object.request}\n""",
            encoding="utf-8",
        )
        (root / "views" / "process.yaml").write_text(
            """id: view.process\nname: Process\nroot: process.handle\nlayout:\n  direction: LR\n  positions:\n    event.message: {x: 120, y: 220}\n    process.handle: {x: 360, y: 220}\n    representation.request-pdf: {x: 360, y: 500}\n""",
            encoding="utf-8",
        )
        return load_repository(root)

    def test_event_and_representation_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repository(Path(tmp))
            errors = [issue for issue in validate(repo) if issue.severity == "error"]
            self.assertEqual([], errors)

    def test_portal_contains_interactive_layout_tools(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self._repository(root)
            output = render_portal(repo, root / "site")
            html = output.read_text(encoding="utf-8")
            self.assertIn("Copy layout YAML", html)
            self.assertIn("Download YAML", html)
            self.assertIn("pointerdown", html)
            self.assertIn("eventKind", html)
            self.assertIn("Representation", html)
            self.assertIn("localStorage", html)


if __name__ == "__main__":
    unittest.main()
