from pathlib import Path
import tempfile
import unittest

from eaops.core import load_repository, validate
from eaops.portal_git import render_portal


class PortalTests(unittest.TestCase):
    def _repository(self, root: Path):
        (root / "model").mkdir()
        (root / "relationships").mkdir()
        (root / "views").mkdir()
        (root / "rules").mkdir()
        (root / "eaops.yaml").write_text(
            """name: Portal Test
repository:
  url: https://github.com/example/ea-repo
  branch: main
metamodel:
  builtin: archimate-3.2
paths:
  model: model
  relationships: relationships
  views: views
  rules: rules
""",
            encoding="utf-8",
        )
        (root / "model" / "business.yaml").write_text(
            """- id: event.message
  type: BusinessEvent
  name: Request Received
  description: Incoming request event.
  properties: {owner: Service, eventKind: message}
- id: process.handle
  type: BusinessProcess
  name: Handle Request
  description: Handle the incoming request.
  properties: {owner: Service, criticality: high}
- id: object.request
  type: BusinessObject
  name: Request
  description: Business information object.
  properties: {owner: Service}
- id: representation.request-pdf
  type: Representation
  name: Request PDF
  description: Human-readable representation.
  properties: {owner: Service, format: PDF}
""",
            encoding="utf-8",
        )
        (root / "relationships" / "relationships.yaml").write_text(
            """- {id: rel.event-process, type: Triggering, source: event.message, target: process.handle}
- {id: rel.process-doc, type: Access, source: process.handle, target: representation.request-pdf}
- {id: rel.doc-object, type: Realization, source: representation.request-pdf, target: object.request}
""",
            encoding="utf-8",
        )
        (root / "views" / "process.yaml").write_text(
            """id: view.process
name: Process
root: process.handle
layout:
  direction: LR
  positions:
    event.message: {x: 120, y: 220}
    process.handle: {x: 360, y: 220}
    representation.request-pdf: {x: 360, y: 500}
""",
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
            self.assertIn("Edit view in GitHub", html)
            self.assertIn("openLayoutInGitHub", html)
            self.assertIn("pointerdown", html)
            self.assertIn("eventKind", html)
            self.assertIn("Representation", html)
            self.assertIn("localStorage", html)


if __name__ == "__main__":
    unittest.main()
