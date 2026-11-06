import copy
import tempfile
from pathlib import Path
import unittest

from eaops.core import RepositoryModel, impact
from eaops.compare import change_impact, compare_repositories
from eaops.render import render_report


def fixture():
    repo = RepositoryModel(Path("."), {})
    kinds = {"platform": "Node", "app": "ApplicationComponent", "process": "BusinessProcess",
             "data": "DataObject", "intent": "Goal", "part": "Node", "writer": "BusinessProcess"}
    repo.objects = {oid: {"id": oid, "name": oid, "type": kind, "properties": {"owner": "A"}} for oid, kind in kinds.items()}
    specs = [("Serving", "platform", "app"), ("Serving", "app", "process"),
             ("Access", "process", "data"), ("Association", "intent", "app"),
             ("Composition", "platform", "part"), ("Access", "writer", "data")]
    for i, (kind, source, target) in enumerate(specs):
        repo.relationships[str(i)] = {"id": str(i), "type": kind, "source": source, "target": target}
    repo.relationships["2"]["properties"] = {"accessType": "read"}
    repo.relationships["5"]["properties"] = {"accessType": "write"}
    return repo


class ImpactTests(unittest.TestCase):
    def test_legacy_connected_component_includes_association(self):
        repo = fixture()
        self.assertEqual(set(repo.objects), set(impact(repo, {"platform"})["impacted"]))

    def test_dependency_direction_and_access(self):
        repo = fixture()
        self.assertEqual({"platform", "app", "process"}, set(impact(repo, {"platform"}, profile="dependency")["impacted"]))
        self.assertEqual({"data", "process"}, set(impact(repo, {"data"}, profile="dependency")["impacted"]))
        self.assertEqual({"writer", "data", "process"}, set(impact(repo, {"writer"}, profile="dependency")["impacted"]))
        self.assertEqual({"part", "platform", "app", "process"}, set(impact(repo, {"part"}, profile="dependency")["impacted"]))

    def test_depth_filter_cycle_and_explanation(self):
        repo = fixture()
        result = impact(repo, {"platform"}, profile="dependency", max_depth=1, explain=True)
        self.assertEqual(["app", "platform"], result["impacted"])
        self.assertEqual({"depth": 1, "via": "platform", "relationship": "0"}, result["reasons"]["app"])
        self.assertEqual(["app"], impact(repo, {"app"}, max_depth=0)["impacted"])
        self.assertEqual(["platform"], impact(repo, {"platform"}, relationship_types=set())["impacted"])
        self.assertEqual({"process", "app", "platform"}, set(impact(repo, {"process"}, direction="incoming", relationship_types={"Serving"})["impacted"]))
        with self.assertRaises(ValueError):
            impact(repo, {"app"}, max_depth=-1)
        with self.assertRaises(ValueError):
            impact(repo, {"app"}, profile="dependency", direction="outgoing")

    def test_metadata_stays_local_deleted_dependencies_remain(self):
        old = fixture()
        new = copy.deepcopy(old)
        new.objects["process"]["properties"]["owner"] = "B"
        self.assertEqual(["process"], change_impact(old, new)["impacted"])
        new = copy.deepcopy(old)
        del new.objects["platform"]
        del new.relationships["0"]
        self.assertEqual({"platform", "app", "process"}, set(change_impact(old, new)["impacted"]))

    def test_inventory_ignores_serialization_sources_and_flags_rules(self):
        old = fixture()
        new = copy.deepcopy(old)
        new.objects["app"]["_source"] = "other.yaml"
        self.assertEqual([], compare_repositories(old, new)["objects"]["modified"])
        new.rules.append({"id": "policy-change"})
        self.assertTrue(change_impact(old, new)["policyReviewRequired"])


class ReportTests(unittest.TestCase):
    def test_indexed_counts_preserve_direction_type_and_duplicates(self):
        repo = fixture()
        repo.relationships["duplicate"] = dict(repo.relationships["1"], id="duplicate")
        with tempfile.TemporaryDirectory() as tmp:
            text = render_report(repo, Path(tmp) / "report.md").read_text()
        self.assertIn("| process | A | — | — | 2 | 1 |", text)
        self.assertIn("| app | A | — | — | 2 |", text)
        self.assertIn("| data | DataObject | A | unclassified | 2 |", text)

    def test_report_does_not_scan_edges_per_application(self):
        class CountingDict(dict):
            calls = 0
            def values(self):
                self.calls += 1
                return super().values()
        repo = fixture()
        repo.relationships = CountingDict(repo.relationships)
        for i in range(1000):
            repo.objects[f"app{i}"] = {"id": f"app{i}", "type": "ApplicationComponent", "name": f"App {i}"}
        with tempfile.TemporaryDirectory() as tmp:
            render_report(repo, Path(tmp) / "report.md")
        self.assertLessEqual(repo.relationships.calls, 4)


if __name__ == "__main__":
    unittest.main()
