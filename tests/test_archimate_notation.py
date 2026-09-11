from pathlib import Path
import tempfile
import unittest

from eaops.core import load_repository
from eaops.repository_portal import render_portal

ROOT = Path(__file__).parents[1] / "examples" / "sample-enterprise"


class ArchiMateNotationTests(unittest.TestCase):
    def test_profile_contains_reference_card_element_families(self):
        repo = load_repository(ROOT)
        expected = {
            "Resource", "Capability", "ValueStream", "CourseOfAction",
            "BusinessActor", "BusinessRole", "BusinessCollaboration", "BusinessInterface",
            "BusinessProcess", "BusinessFunction", "BusinessInteraction", "BusinessEvent",
            "BusinessService", "BusinessObject", "Contract", "Representation", "Product",
            "ApplicationComponent", "ApplicationCollaboration", "ApplicationInterface",
            "ApplicationFunction", "ApplicationInteraction", "ApplicationProcess",
            "ApplicationEvent", "ApplicationService", "DataObject",
            "Node", "Device", "SystemSoftware", "TechnologyCollaboration", "TechnologyInterface",
            "Path", "CommunicationNetwork", "TechnologyFunction", "TechnologyProcess",
            "TechnologyInteraction", "TechnologyEvent", "TechnologyService", "Artifact",
            "Equipment", "Facility", "DistributionNetwork", "Material",
            "Stakeholder", "Driver", "Assessment", "Goal", "Outcome", "Principle",
            "Requirement", "Constraint", "Meaning", "Value",
            "WorkPackage", "Deliverable", "ImplementationEvent", "Plateau", "Gap",
            "Grouping", "Location", "Junction",
        }
        self.assertTrue(expected <= set(repo.metamodel["elementTypes"]))

    def test_profile_contains_reference_card_relationship_families(self):
        repo = load_repository(ROOT)
        expected = {
            "Composition", "Aggregation", "Assignment", "Realization", "Serving",
            "Access", "Influence", "Triggering", "Flow", "Specialization", "Association",
        }
        self.assertTrue(expected <= set(repo.metamodel["relationshipTypes"]))

    def test_generated_portal_has_semantic_notation_and_layout_tools(self):
        repo = load_repository(ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            html = render_portal(repo, Path(tmp)).read_text(encoding="utf-8")
        for token in (
            "ArchiMate notation library", "BusinessEvent", "Representation", "ApplicationComponent",
            "TechnologyEvent", "ImplementationEvent", "Composition", "Aggregation", "Specialization",
            "accessType", "diamondFilled", "triangleOpen", "pointerdown", "localStorage",
            "Copy layout YAML", "Download YAML", "Edit view in GitHub", "Reset to Git",
        ):
            self.assertIn(token, html)


if __name__ == "__main__":
    unittest.main()
